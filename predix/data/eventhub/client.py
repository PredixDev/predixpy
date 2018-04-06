import json
import logging
import os
import threading
import time

import grpc

import predix.config
import predix.service
from predix.data.eventhub import Health_pb2_grpc
from predix.data.eventhub import Health_pb2
from predix.data.eventhub.publisher import PublisherConfig, Publisher
from predix.data.eventhub.subscriber import Subscriber


class EventHubException(Exception):
    def __init__(self, str):
        Exception.__init__(self, str)


class Eventhub(object):
    """
    Client library for working with the Eventhub Service
    Provide it with the id, and the config you need for each thing
    if that feature is not required then leave config as None
    """

    def __init__(self,
                 publish_config=None,
                 subscribe_config=None,
                 ):
        # initialize the publisher and subscriber
        # only build shared grpc channel if required
        self._ws = None
        self._channel = None
        self._run_health_checker = True
        if publish_config is not None:
            # make the channel
            if publish_config.protocol == PublisherConfig.Protocol.GRPC:
                self._init_channel()
            self.publisher = Publisher(eventhub_client=self, channel=self._channel, config=publish_config)

        if subscribe_config is not None:
            if self._channel is None:
                self._init_channel()
            self.subscriber = Subscriber(self, channel=self._channel, config=subscribe_config)

    def shutdown(self):
        """
        Shutdown the client, shutdown the sub clients and stop the health checker
        :return: None
        """
        self._run_health_checker = False
        if self.publisher is not None:
            self.publisher.shutdown()

        if self.subscriber is not None:
            self.subscriber.shutdown()

    def _get_host(self):
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            host = services['predix-event-hub'][0]['credentials']['publish']['protocol_details']['uri']
            return host[:host.index(':')]
        return self.get_service_env_value('host')

    def _get_grpc_port(self):
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            host = services['predix-event-hub'][0]['credentials']['publish']['protocol_details']['uri']
            return host[host.index(':')+1:]
        return self.get_service_env_value('port')

    def get_service_env_value(self, key):
        """
        Get a env variable as defined by the service admin
        :param key: the base of the key to use
        :return: the env if it exists
        """
        service_key = predix.config.get_env_key(self, key)
        value = os.environ[service_key]
        if not value:
            raise ValueError("%s env unset" % key)
        return value

    def _init_channel(self):
        """
        build the grpc channel used for both publisher and subscriber
        :return: None
        """
        host = self._get_host()
        port = self._get_grpc_port()

        if 'TLS_PEM_FILE' in os.environ:
            with open(os.environ['TLS_PEM_FILE'], mode='rb') as f:  # b is important -> binary
                file_content = f.read()
            credentials = grpc.ssl_channel_credentials(root_certificates=file_content)
        else:
            credentials = grpc.ssl_channel_credentials()

        self._channel = grpc.secure_channel(host + ":" + port, credentials=credentials)
        self._init_health_checker()

    def _init_health_checker(self):
        """
        start the health checker stub and start a thread to ping it every 30 seconds
        :return: None
        """
        stub = Health_pb2_grpc.HealthStub(channel=self._channel)
        self._health_check = stub.Check
        health_check_thread = threading.Thread(target=self._health_check_thread)
        health_check_thread.daemon = True
        health_check_thread.start()

    def _health_check_thread(self):
        """
        Health checker thread that pings the service every 30 seconds
        :return: None
        """
        while self._run_health_checker:
            response = self._health_check(Health_pb2.HealthCheckRequest(service='predix-event-hub.grpc.health'))
            logging.debug('received health check: ' + str(response))
            time.sleep(30)
        return

    class GrpcManager:
        """
        Class for managing GRPC calls by turing the generators grpc uses into function calls
        This allows the sdk to man in the middle the messages
        """
        def __init__(self, stub_call, on_msg_callback, metadata, tx_stream=True, initial_message=None):
            """
            :param stub_call: the call on the grpc stub to build the generator on
            :param on_msg_callback: the callback to pass any received functions on
            :param metadata: metadata to attach to the stub call
            """
            self._tx_stream = tx_stream
            self._stub_call = stub_call
            self._on_msg_callback = on_msg_callback
            self._metadata = metadata
            self._initial_message = initial_message
            self._grpc_rx_thread = threading.Thread(target=self._grpc_rx_receiver)
            self._grpc_rx_thread.daemon = True
            self._grpc_rx_thread.start()
            self._grpc_tx_queue = []
            self._run_generator = True
            time.sleep(1)

        def send_message(self, tx_message):
            """
            Add a message onto the tx queue to be sent on the stub
            :param tx_message:
            :return: None
            """
            self._grpc_tx_queue.append(tx_message)

        def _grpc_rx_receiver(self):
            """
            Blocking Function that opens the stubs generator and pass any messages onto the callback
            :return: None
            """
            logging.debug("grpc rx stream metadata: " + str(self._metadata))
            if self._tx_stream:
                if self._initial_message is not None:
                    self.send_message(self._initial_message)
                msgs = self._stub_call(request_iterator=self._grpc_tx_generator(), metadata=self._metadata)
            else:
                msgs = self._stub_call(self._initial_message, metadata=self._metadata)

            for m in msgs:
                self._on_msg_callback(m)

        def stop_generator(self):
            """
            Call this to close the generator
            :return:
            """
            logging.debug('stopping generator')
            self._run_generator = False

        def _grpc_tx_generator(self):
            """
            the generator taking and messages added to the grpc_tx_queue
            and yield them to grpc
            :return: grpc messages
            """
            while self._run_generator:
                while len(self._grpc_tx_queue) != 0:
                    yield self._grpc_tx_queue.pop(0)
            return

