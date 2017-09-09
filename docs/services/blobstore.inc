
Blob Store
----------

The Blob Store Service is a persistent store for binary large objects such as
files and images.  You can learn more from the `Blob Store`_ catalog page and
official documentation.

.. _Blob Store: https://www.predix.io/services/service.html?id=1179

Example
.......

Here is a simple demo to create a blob store instance and basic use example of
listing files.

::

    # How-To Create the service
    # IMPORTANT: You must have already configured UAA and client

    import predix.admin.app
    app = predix.admin.app.Manifest()
    app.create_blobstore()


::

    # How-To Use the Service
    # IMPORTANT: this must be run in Cloud Foundry so
    # this example is using Flask methods

    import predix.app
    app = predix.app.Manifest()
    blobstore = app.get_blobstore()

    @api.route('/list')
    def list():
        objs = blobstore.list_objects()
        return jsonify(objs)

Find more examples with :ref:`blobstore-cookbook` (including the rest of the
code for this example).

Boto 3
......

For US-WEST on AWS all the functionality of Boto 3 is exposed by referencing
``blobstore.client``.  You can find more about those methods directly from the
Boto3 Documentation:

https://boto3.readthedocs.io/

Blob Store API
..............

.. automodule:: predix.data.blobstore
    :members:

Blob Store Administration
..........................

.. automodule:: predix.admin.blobstore
    :members:
