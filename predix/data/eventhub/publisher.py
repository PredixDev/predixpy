import json
import logging
import threading
import websocket

import time

from predix.data.eventhub import EventHub_pb2, EventHub_pb2_grpc, grpc_manager


class PublisherConfig:
    """
    object to store the publisher config
    as well as some of the enums for the settings
    """

    class AcknowledgementOptions:
        def __init__(self):
            pass

        NACKS_ONLY = 'NACKS_ONLY'
        ACKS_AND_NACKS = 'ACKS_AND_NACKS'
        NONE = 'NONE'

    class Protocol:
        def __init__(self):
            pass

        WSS = 'WSS'
        GRPC = 'GRPC'

    class Type:
        def __init__(self):
            pass

        ASYNC = 'ASYNC'
        SYNC = 'SYNC'

    def __init__(self,
                 topic="",
                 publish_type=Type.ASYNC,
                 sync_timeout=15,
                 protocol=Protocol.GRPC,
                 async_cache_ack_interval_millis=500,
                 async_cache_acks_and_nacks=True,
                 async_acknowledgement_options=AcknowledgementOptions.ACKS_AND_NACKS,
                 async_auto_send=False,
                 async_auto_send_amount=100,
                 async_auto_send_interval_millis=10000):
        """

        :param topic: str the topic to publish to
        :param publish_type: the type of publisher you want to make. sync means publish is a blocking call
        :param sync_timeout: timeout length to wait for acks
        :param protocol: the protocol for publishing messages, WSS or GRPC
        :param async_cache_ack_interval_millis:
        :param async_cache_acks_and_nacks: should service cache the acks
        :param async_acknowledgement_options: what acks should be received
        :param async_auto_send: should the skd auto send messages
        :param async_auto_send_amount: after how many messages should messages be automatically sent
        :param async_auto_send_interval_millis: what is the max period between messages
        """

        self.topic = topic
        self.protocol = protocol
        self.publish_type = publish_type

        # Async config options
        self.async_cache_ack_interval_millis = async_cache_ack_interval_millis
        self.async_cache_acks_and_nacks = async_cache_acks_and_nacks
        if async_acknowledgement_options == self.AcknowledgementOptions.ACKS_AND_NACKS:
            self.async_enable_acks = True
            self.async_enable_nacks_only = False
        elif async_acknowledgement_options == self.AcknowledgementOptions.NACKS_ONLY:
            self.enable_acks = False
            self.enable_nacks_only = True
        elif async_acknowledgement_options == self.AcknowledgementOptions.NONE:
            self.async_enable_acks = False
            self.async_enable_nacks_only = False
        self.async_auto_send = async_auto_send
        self.async_auto_send_amount = async_auto_send_amount
        self.async_auto_send_interval_millis = async_auto_send_interval_millis

        # sync config options
        self.sync_timeout = sync_timeout

    def is_grpc(self):
        return self.protocol == self.Protocol.GRPC

    def is_wss(self):
        return self.protocol == self.Protocol.WSS

    def is_async(self):
        return self.publish_type == self.Type.ASYNC

    def is_sync(self):
        return self.publish_type == self.Type.SYNC


class Publisher:
    """
    Publisher Object for both grpc and web socket
    """

    def __init__(self, eventhub_client, config, channel=None):
        self.eventhub_client = eventhub_client
        self._channel = channel
        self.config = config
        self._ws = None
        if config.is_wss():
            self._init_publisher_ws()
        else:
            if channel is None:
                raise ValueError("must provide channel if using grpc to publish")
            self._init_grpc_publisher()

        # Operational
        self._rx_queue = []
        self._tx_queue = []
        self._tx_queue_lock = threading.Lock()
        self.callback = None
        self.last_send_time = 0
        self._run_ack_generator = True
        self._active = True

        if config.async_auto_send:
            t = threading.Thread(target=self._auto_send)
            t.daemon = True
            t.start()

    def __del__(self):
        """
        Destructor to make sure an open web socket connection is closed.
        """
        if self._active:
            if self._ws is not None:
                logging.debug("closing websocket")
                self._ws.close()
                logging.debug("waiting on websocket thread to exit")
                self._ws_thread.join()
            else:
                logging.debug("stopping generators")
                self.grpc_manager.stop_generator()
                self._run_ack_generator = False

    """
    ####################################################################################
    User Code
    ####################################################################################
    """

    def shutdown(self):
        """
        shutdown the client, stops the web socket or grpc threads
        :return:
        """
        if self._active:
            if self._ws is not None:
                logging.debug("closing web socket")
                self._ws.close()
                logging.debug("waiting on webs ocket thread to exit")
                self._ws_thread.join()
                self._ws = None
            else:
                logging.debug("stopping generators")
                self.grpc_manager.stop_generator()
                self._run_ack_generator = False
        self._active = False

    def add_message(self, id, body, tags=False):
        """
        add messages to the rx_queue
        :param id: str message Id
        :param body: str the message body
        :param tags: dict[string->string] tags to be associated with the message
        :return: self
        """
        if not tags:
            tags = {}
        try:
            self._tx_queue_lock.acquire()
            self._tx_queue.append(
                EventHub_pb2.Message(id=id, body=body, tags=tags, zone_id=self.eventhub_client.zone_id))
        finally:
            self._tx_queue_lock.release()
        return self

    def publish_queue(self):
        """
        Publish all messages that have been added to the queue for configured protocol
        :return: None
        """
        self.last_send_time = time.time()
        try:
            self._tx_queue_lock.acquire()
            start_length = len(self._rx_queue)
            publish_amount = len(self._tx_queue)
            if self.config.protocol == PublisherConfig.Protocol.GRPC:
                self._publish_queue_grpc()
            else:
                self._publish_queue_wss()
            self._tx_queue = []
        finally:
            self._tx_queue_lock.release()

        if self.config.publish_type == self.config.Type.SYNC:
            start_time = time.time()
            while time.time() - start_time < self.config.sync_timeout and \
                                    len(self._rx_queue) - start_length < publish_amount:
                pass
            return self._rx_queue

    def ack_generator(self):
        """
        generator for acks to yield messages to the user in a async configuration
        :return: messages as they come in
        """
        if self.config.is_sync():
            logging.warning('cant use generator on a sync publisher')
            return
        while self._run_ack_generator:
            while len(self._rx_queue) != 0:
                logging.debug('yielding to client')
                yield self._rx_queue.pop(0)
        return

    """
    ####################################################################################
    Internal
    ####################################################################################
    """

    def _auto_send(self):
        """
        auto send blocking function, when the interval or the message size has been reached, publish
        :return:
        """
        while True:
            if time.time() - self.last_send_time > self.config.async_auto_send_interval_millis or \
                            len(self._tx_queue) >= self.config.async_auto_send_amount:
                self.publish_queue()

    def _generate_publish_headers(self):
        """
        generate the headers for the connection to event hub service based on the provided config
        :return: {} headers
        """
        headers = {
            'predix-zone-id': self.eventhub_client.zone_id
        }
        token = self.eventhub_client.service._get_bearer_token()
        if self.config.is_grpc():
            headers['authorization'] = token[(token.index(' ') + 1):]
        else:
            headers['authorization'] = token

        if self.config.topic == '':
            headers['topic'] = self.eventhub_client.zone_id + '_topic'
        else:
            headers['topic'] = self.config.topic

        if self.config.publish_type == self.config.Type.SYNC:
            headers['sync-acks'] = 'true'
        else:
            headers['sync-acks'] = 'false'
            headers['send-acks-interval'] = str(self.config.async_cache_ack_interval_millis)
            headers['acks'] = str(self.config.async_enable_acks).lower()
            headers['nacks'] = str(self.config.async_enable_nacks_only).lower()
            headers['cache-acks'] = str(self.config.async_cache_acks_and_nacks).lower()
        return headers

    def _publisher_callback(self, publish_ack):
        """
        publisher callback that grpc and web socket can pass messages to
        address the received message onto the queue
        :param publish_ack: EventHub_pb2.Ack the ack received from either wss or grpc
        :return: None
        """
        logging.debug("ack received: " + str(publish_ack).replace('\n', ' '))
        self._rx_queue.append(publish_ack)

    """
    ####################################################################################
    GRPC  Code
    ####################################################################################
    """

    def _init_grpc_publisher(self):
        """
        initialize the grpc publisher, builds the stub and then starts the grpc manager
        :return: None
        """
        self._stub = EventHub_pb2_grpc.PublisherStub(channel=self._channel)
        self.grpc_manager = grpc_manager.GrpcManager(stub_call=self._stub.send,
                                                 on_msg_callback=self._publisher_callback,
                                                 metadata=self._generate_publish_headers().items())

    def _publish_queue_grpc(self):
        """
        send the messages in the tx queue to the GRPC manager
        :return: None
        """
        messages = EventHub_pb2.Messages(msg=self._tx_queue)
        publish_request = EventHub_pb2.PublishRequest(messages=messages)
        self.grpc_manager.send_message(publish_request)

    """
    ####################################################################################
    Web Socket Code
    ####################################################################################
    """

    def _publish_queue_wss(self):
        """
        send the messages down the web socket connection as a json object
        :return: None
        """

        msg = []
        for m in self._tx_queue:
            msg.append({'id': m.id, 'body': m.body, 'zone_id': m.zone_id})
        self._ws.send(json.dumps(msg), opcode=websocket.ABNF.OPCODE_BINARY)

    def _init_publisher_ws(self):
        """
        Create a new web socket connection with proper headers.
        """
        logging.debug("Initializing new web socket connection.")

        url = ('wss://%s/v1/stream/messages/' % self.eventhub_client.host)

        headers = self._generate_publish_headers()

        logging.debug("URL=" + str(url))
        logging.debug("HEADERS=" + str(headers))

        websocket.enableTrace(False)
        self._ws = websocket.WebSocketApp(url,
                                          header=headers,
                                          on_message=self._on_ws_message,
                                          on_open=self._on_ws_open,
                                          on_close=self._on_ws_close)
        self._ws_thread = threading.Thread(target=self._ws.run_forever, kwargs={'ping_interval': 30})
        self._ws_thread.daemon = True
        self._ws_thread.start()
        time.sleep(1)

    def _on_ws_message(self, ws, message):
        """
        on_message callback of websocket class, load the message into a dict and then
        update an Ack Object with the results
        :param ws: web socket connection that the message was received on
        :param message: web socket message in text form
        :return: None
        """
        logging.debug(message)
        json_list = json.loads(message)
        for rx_ack in json_list:
            ack = EventHub_pb2.Ack()
            for key, value in rx_ack.items():
                setattr(ack, key, value)
            self._publisher_callback(ack)

    def _on_ws_open(self, ws):
        """
        on open callback of websocket connection
        :param ws: web socket connection that the message was received on
        :return: None
        """
        logging.debug("ws web socket connected")
        pass

    def _on_ws_error(self, ws, error):
        """
        on error callback of web socket error
        :param ws: web socket connection that the message was received on
        :param error:
        :return:
        """
        logging.debug(error)
        pass

    def _on_ws_close(self, ws):
        """
        on close callback of websocket class
        :param ws:  web socket connection that the message was received on
        :return: None
        """
        logging.debug("ws connection closed")
        pass
