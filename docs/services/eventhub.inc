
Event Hub
---------

Event Hub uses gRPC for publishing and subscribing messages.  A full-duplex
streaming RPC framework, gRPC uses protocol buffers for wire protocol
implemented over HTTP/2 and using header compression, multiplexing TCP
connections, and flow control.  Protocol Buffers is a binary protocol further
suited for IoT devices that publish high-velocity data over networks with low
bandwidth.

For more details see the official `Event Hub`_ service documentation.

.. _Event Hub: https://docs.predix.io/en-US/content/service/data_management/event_hub/

Example
.......

Here is a simple demo to create a service instance.

::

    # How-To Create the service
    # IMPORTANT: You must have already configured UAA and client

    import predix.admin.app
    admin = predix.admin.app.Manifest()
    admin.create_eventhub(publish=True, subscribe=True)

::

    # How-To Publish Messages

    import predix.app
    app = predix.app.Manifest()
    eh = app.get_eventhub()

    acks = {}
    for i in range(10, 0, -1):
        msg_id = str(i)
        msg_body = 'Hello World {}'.format(msg_id)
        eh.publisher.add_message(msg_id, msg_body)

        acks[msg_id] = False

    print("Publishing messages.")
    eh.publisher.publish_queue()

    for response in eh.publisher.ack_generator():
        for ack in response.ack:
            msg_id = ack.id
            print("Message {} acknowledged.".format(msg_id))
            del acks[msg_id]

        if not acks.keys():
            print("All messages delivered.")
            break

::

    # How-To Subscribe Messages

    import predix.app
    app = predix.app.Manifest()
    eh = app.get_eventhub()

    for msg in eh.subscriber.subscribe():
        print(msg)

Find more examples :ref:`eventhub-cookbook`.

Event Hub API
.............

.. automodule:: predix.data.eventhub
    :members:

Event Hub Administration
........................

.. automodule:: predix.admin.eventhub
    :members:

