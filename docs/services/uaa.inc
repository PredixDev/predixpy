
User Accounts and Authentication
--------------------------------

The User Accounts and Authentication Service, known as UAA, is an OAuth2
implementation common in Cloud Foundry deployments.  You can learn more about
it from the `UAA`_ catalog page and official documentation.

.. _UAA: https://www.predix.io/services/service.html?id=1172

.. hint::

    You will need UAA to work with most Predix services including Asset, Time
    Series, and ACS.

Example
.......

Here is a simple demo to create a uaa instance, create a client, authenticate
as the client, and print out the scopes.

::

    # How-To Create the Service

    import predix.admin.app
    app = predix.admin.app.Manifest()
    app.create_uaa('admin-secret')
    app.create_client('my-client', 'my-client-secret')

::

    # How-To Use the Service

    import predix.app
    app = predix.app.Manifest()
    uaa = app.get_uaa()
    uaa.authenticate('my-client', 'my-client-secret')
    print(uaa.get_scopes())

Find more examples with :ref:`uaa-cookbook`.

Authentication
..............

*Is the username and password provided correct?*

If so, those credentials can be authenticated and a token generated for proving
that the identify is verified.  This token is used in any subsequent service
calls in the header of those requests.  The Predix Python SDK takes care of
this transparently for you.

The username and password can be provided by an actual end "user", an
application that is a "client", or the "admin" user managing your cloud foundry
space.

Expiration
..........

The token is only valid for a period of time so the Predix Python SDK tries to
manage this and only requests a new token if you explicitly logout a session to
invalidate a token or if you reach the expiration period.

Authorization
.............

*That authenticated token, is it allowed to talk to this other service?*

Cloud Foundry and UAA have a sophisticated system of managing scopes and
authorities for what a user or client are able to do.  Since most services only
support coarse grained permissions such as read/write the Predix Python SDK
manages the details with a ``grant_client()`` method for each service.  If any
options are meaningful they are generally exposed.

UAA API
.......

.. automodule:: predix.security.uaa
    :members:

UAA Administration
..................

.. automodule:: predix.admin.uaa
    :members:

