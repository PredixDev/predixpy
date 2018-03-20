
.. _asset-service:

Asset
-----

The Predix Asset Service provides a persistent store for graph data about
physical assets, their properties, and relationships.  You can learn more about
it from the `Asset`_ catalog page and official documentation.

.. _Asset: https://www.predix.io/services/service.html?id=1171

Example
.......

Here is a simple demo to create and use the Predix Asset service.

::

    # How-To Create the Service
    # IMPORTANT: You must have already configured UAA and client

    import predix.admin.app
    admin = predix.admin.app.Manifest()
    admin.create_asset()

::

    # How-To Use the Service

    import predix.app
    app = predix.app.Manifest()
    asset = app.get_asset()

    volcano = {
        'uri': '/volcano/masaya',
        'name': 'Masaya',
        'location': {
            'lat': 11.98531829999,
            'long': -86.1783429000,
        },
        'description': 'Near Masaya, Nicaragua',
    }
    asset.post_collection('/volcano', [volcano])
    print(asset.get_collection('/volcano/masaya'))

Find more examples with :ref:`asset-cookbook`.

Asset Collections
.................

Assets are organized into collections and the Predix Python SDK attempts to
help manage collections with an ``AssetCollections`` class that acts for doing
object relationship mapping to marshall Python Domain objects into the Predix
Asset Service.

Asset API
.........

.. automodule:: predix.data.asset
    :members:

Asset Administration
.....................

.. automodule:: predix.admin.asset
    :members:
