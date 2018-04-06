
.. _asset-cookbook:

Asset Recipes
-------------

Recipes for working with Predix Python SDK and the Asset service.

It is expected you used the SDK to create the service so that it is configured
by Manifest.

How-To Get a Unique URI
.......................

The Predix Asset Service requires a ``uri`` as part of the body whenever you
post a collection.  The ``predix.data.asset.AssetCollection`` class will help
generate this for you but sometimes you want to do that for yourself.

::

    import predix.app
    app = predix.app.Manifest()
    asset = app.get_asset()

    guid = asset.get_guid() # e36af84e-95a9-485b-993d-e2004427d73e
    uri = asset.get_guid('/volcano') # /volcano/44c99f3b-aa1b-486c-9a9d-14740b600313


