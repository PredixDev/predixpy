
.. _errors-cookbook:

Error Recipes
-------------

Recipes for debugging and resolving common errors and issues you may run into
using the Predix Python SDK.

How-To Turn Logging On
......................

You can directly use the Python `logging` library to set different logging
levels such as ``DEBUG`` or ``INFO``.  This is a useful way to find details
about the underlying service calls.

::

    import logging
    logging.basicConfig(level=logging.DEBUG)

Enabling DEBUG will output the details of the requests such as URI, Headers,
Body, and Response.

.. parsed-literal::

    DEBUG:root:URI=https://predix-asset.run.aws-usw02-pr.ice.predix.io/v1/volcano
    DEBUG:root:HEADERS={'Predix-Zone-Id': '******************', 'Content-Type':
        'application/json', 'Authorization': u'Bearer ********', 'Accept': 'application/json'}
    DEBUG:urllib3.connectionpool:https://predix-asset.run.aws-usw02-pr.ice.predix.io:443
    "GET /v1/volcano HTTP/1.1" 200 170
    DEBUG:root:STATUS=200


How-To Fix HTTPSConnectionPool Error
....................................

If you see a HTTPSConnectionPool exception like the following:

.. parsed-literal::

    HTTPSConnectionPool(host='predix-asset.run.aws-usw02-pr.ice.predix.io',
    port=443): Max retries exceeded with url: /v1/volcano (Caused by
    ProxyError('Cannot connect to proxy.',
        NewConnectionError('<urllib3.connection.VerifiedHTTPSConnection object
            at 0x10c85c410>: Failed to establish a new connection: [Errno 8]
            nodename nor servname provided, or not known',)))

This is likely to be a proxy error.  You may need to set or unset your
``HTTPS_PROXY`` variables to resolve.

