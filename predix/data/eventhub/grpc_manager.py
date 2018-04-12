import threading
import time
import logging 

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

