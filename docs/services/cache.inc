
Predix Cache
------------

The Predix Cache Service provides an instance of Redis, key-value memory store,
for use in building applications.  You can learn more about it from the `Predix
Cache`_ catalog page and official documentation.

.. _Predix Cache: https://www.predix.io/services/service.html?id=1215

.. hint::

    You will need to push an app to the Predix Cloud to make use of this
    service since firewall access is blocked otherwise.

Example
.......

Here is a simple demo to create the service.

::

    # How-To Create the service

    import predix.admin.app
    admin = predix.admin.app.Manifest()
    admin.create_cache()

Find more examples in :ref:`cache-cookbook`.

Predix Cache API
................

.. automodule:: predix.data.cache
    :members:

Predix Cache Administration
...........................

.. automodule:: predix.admin.cache
    :members:

