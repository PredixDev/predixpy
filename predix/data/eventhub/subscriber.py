from predix.data.eventhub import EventHub_pb2, EventHub_pb2_grpc
from predix.data.eventhub.client import Eventhub


class SubscribeConfig:
    class Recency:
        def __init__(self):
            pass

        OLDEST = "Oldest"
        NEWEST = "Newest"

    def __init__(self,
                 subscriber_name='predix_py_subscriber',
                 batching_enabled=False,
                 auto_send_acks=False,
                 batch_size=100,
                 batch_interval_millis=10000,
                 acks_enabled=False,
                 recency=Recency.OLDEST,
                 ack_duration_before_retry_seconds=30,
                 ack_max_retries=10,
                 ack_retry_interval_seconds=30,
                 topics=None):
        """
        Subscribe Config
        :param subscriber_name: The name of the subscriber
        :param batching_enabled: Should the messages be delivered in batches
        :param batch_size: If batching, what should be the size of the batches
        :param batch_interval_millis: If batching, what should be the max interval
        :param acks_enabled: should the service be expecting acks on delivered messages
        :param ack_duration_before_retry_seconds:  How long should the service wait for an ack before it retry
        :param ack_max_retries: How many retries should the service wait for
        :param ack_retry_interval_seconds: after the initial retry, what should be the period of the message retry
        :param recency: What messages should be sent when connected, all messages in the queue or only new messages
        :param topics: What topics should be subscribed too
        """
        self.subscriber_name = subscriber_name
        self.batching_enabled = batching_enabled
        self.batch_size = batch_size
        self.batch_interval_millis = batch_interval_millis
        self.acks_enabled = acks_enabled
        self.recency = recency
        self.ack_duration_before_retry_seconds = ack_duration_before_retry_seconds
        self.ack_max_retries = ack_max_retries
        self.ack_retry_interval_seconds = ack_retry_interval_seconds
        self.topics = topics if topics is not None else []
        if topics is not None:
            raise
class Subscriber:
    def __init__(self, eventhub_client, config, channel):
        self.eventhub_client = eventhub_client
        self._config = config
        self._stub = EventHub_pb2_grpc.SubscriberStub(channel=channel)

        tx_stream = True
        initial_message = None
        if self._config.batching_enabled:
            stub_call = self._stub.subscribe
        elif self._config.acks_enabled:
            stub_call = self._stub.receiveWithAcks
        else:
            stub_call = self._stub.receive
            tx_stream = False
            initial_message = EventHub_pb2.SubscriptionRequest(subscriber=self._config.subscriber_name,
                                                               zone_id=self.eventhub_client.zone_id,
                                                               instance_id='predixpy-subscriber')
        self._rx_messages = []
        self.active = True
        self.run_subscribe_generator = True
        self.grpc_manager = Eventhub.GrpcManager(stub_call=stub_call,
                                                 on_msg_callback=self._subscriber_callback,
                                                 metadata=self._generate_subscribe_headers(),
                                                 tx_stream=tx_stream,
                                                 initial_message=initial_message
                                                 )

    def __del__(self):
        self.grpc_manager.stop_generator()
        self.run_subscribe_generator = False
        self.active = False

    def shutdown(self):
        if self.active:
            self.active = False
            self.grpc_manager.stop_generator()
            self.run_subscribe_generator = False

    def _subscriber_callback(self, rx_message):
        """
        subscriber callback for the GRPC manager, appends them onto the queue
        :param rx_message: SubscriptionMessage or Message
        :return: None
        """
        self._rx_messages.append(rx_message)

    def subscribe(self):
        """
        return a generator for all subscribe messages
        :return: None
        """
        while self.run_subscribe_generator:
            if len(self._rx_messages) != 0:
                yield self._rx_messages.pop(0)
        return

    def send_acks(self, message):
        """
        send acks to the service
        :param message: EventHub_pb2.Message
        :return: None
        """
        if isinstance(message, EventHub_pb2.Message):
            ack = EventHub_pb2.Ack(partition=message.partition, offset=message.offset)
            self.grpc_manager.send_message(EventHub_pb2.SubscriptionResponse(ack=ack))

        elif isinstance(message, EventHub_pb2.SubscriptionMessage):
            acks = []
            for m in message.messages:
                acks.append(EventHub_pb2.Ack(parition=m.partition, offset=m.offset))
            self.grpc_manager.send_message(EventHub_pb2.SubscriptionAcks(ack=acks))

    def _generate_subscribe_headers(self):
        """
        generate the subscribe stub headers based on the supplied config
        :return: i
        """
        headers =[]
        headers.append(('predix-zone-id', self.eventhub_client.zone_id))

        token = self.eventhub_client.service._get_bearer_token()
        headers.append(('subscribername', self._config.subscriber_name))
        headers.append(('authorization', token[(token.index(' ') + 1):]))

        if self._config.topics is []:
            headers.append(('topic', self.eventhub_client.zone_id + '_topic'))
        else:
            for topic in self._config.topics:
                headers.append(('topic', topic))

        headers.append(('offset-newest', str(self._config.recency == self._config.Recency.NEWEST).lower()))

        headers.append(('acks', str(self._config.acks_enabled).lower()))
        if self._config.acks_enabled:
            headers.append(('max-retries', str(self._config.ack_max_retries)))
            headers.append(('retry-interval', str(self._config.ack_retry_interval_seconds) + 's'))
            headers.append(('duration-before-retry', str(self._config.ack_duration_before_retry_seconds) + 's'))

        if self._config.batching_enabled:
            headers.append(('batch-size', str(self._config.batch_size)))
            headers.append(('batch-interval', str(self._config.batch_interval_millis) + 'ms'))

        return headers


def __del__(self):
    """
    Destructor to make sure an open web socket connection is closed.
    """
    self.shutdown()
