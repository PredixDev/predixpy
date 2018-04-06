
.. _uaa-cookbook:

UAA Recipes
-----------

Recipes for working with Predix Python SDK and the UAA service.

It is expected you already used the SDK to create the service so that it is
configured by Manifest.

How-To Get Scopes for a Given Client
....................................

You want to verify the scopes and authorities for a client.

::

   import predix.app
   app = predix.app.Manifest()

   uaa = app.get_uaa()
   uaa.authenticate(client_id, client_secret)
   print(uaa.get_scopes())

How-To Get the Token for a Client/User
......................................

Typically this is unnecessary when using the SDK as the headers including the
token are generated for you.  This is how it works though:

::

    import predix.app
    app = predix.app.Manifest()

    uaa = app.get_uaa()
    uaa.authenticate(user_id, user_secret)
    print(uaa.get_token())

How-To Add Scopes or Authorities for a Client/User
..................................................

Typically this is unnecessary when using the SDK as scopes/authorities for each
service are granted when they are created, but there may be cases you need to
work around default behaviors.  This is how you can do it:

::

    import predix.admin.uaa

    uaa = predix.admin.uaa.UserAccountAuthentication()
    uaa.authenticate()
    scopes = ['uaa.resource']
    authorities = ['uaa.resource']
    uaa.update_client_grants(client_id, scope=scopes, authorities=authorities)

If you want to completely replace scopes and authorities you can add an
optional ``replace=True``.

How-To Create a Superuser Client
................................

You can typically get by with just the **admin** user account, but if you
wanted to create a separate superuser that can manage clients.

::

    import predix.admin.app
    app = predix.admin.app.Manifest()
    uaa = app.get_uaa()
    uaa.authenticate('admin', 'your-admin-secret')

    uaa.create_client('superuser', 'superuser-secret')
    uaa.grant_client_permissions('superuser', admin=True)
    print(uaa.get_clients())

How-To Create Users
...................

In order to create users you must have a client with permission to do so.

::

    import predix.admin.app
    app = predix.admin.app.Manifest()
    app.create_client('usermanager', 'userman-secret')
    app.grant_scim_permissions('usermanager', read=True, write=True)

Once you have that client with scim permissions you can begin modifying users.

::

    import predix.app
    app = predix.app.Manifest()
    uaa = app.get_uaa()
    uaa.authenticate(app.get_client_id(), app.get_client_secret())
    uaa.create_user('j12y', 'password123', 'DeLancey', 'Jayson',
        'volcano@ge.com')

How-To Debug a 403 Forbidden Client Error
.........................................

If you get a Forbidden for url error with UAA that looks something like the
following you will need to fix permissions.

.. parsed-literal::

    requests.exceptions.HTTPError: 403 Client Error: Forbidden for url:
    https://****.predix-uaa.run.aws-usw02-pr.ice.predix.io/userinfo

This could happen if the client making the request does not have sufficient
scopes and authorities.  For example, a request for that endpoint requires the
``openid`` scope.  You can do something like the following if UAA is setup with
an admin and client already to extend that clients permissions:

::

    import predix.app
    app = predix.app.Manifest()
    uaa = app.get_uaa()
    uaa.authenticate('admin', 'your-admin-secret')
    uaa.grant_scim_permissions(app.get_client(), openid=True)
    uaa.authenticate(app.get_client_id(), app.get_client_secret(),
        use_cache=False)

Note that the ``use_cache=False`` is there because if you already have
authenticated as a client the token remains cached until it expires.  You'll
need a new token anytime you modify scopes and authorities.

