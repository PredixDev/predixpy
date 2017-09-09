
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

