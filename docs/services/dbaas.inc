
Predix DBaaS
------------

The Predix Database as a Service provides an instance of PostgreSQL, a
relational database management system for persisting data needed in building
applications.  You can learn more about it from the `Predix Database as a
Service`_ catalog page and official documentation.

.. _Predix Database as a Service: https://www.predix.io/services/service.html?id=1178

.. hint::

    You will need to push an app to the Predix Cloud to make use of this
    service since firewall access is blocked otherwise.

Example
.......

Here is a simple demo to create and use the service.

::

    # How-To Create the service

    import predix.admin.app
    admin = predix.admin.app.Manifest()
    admin.create_dbaas()

::

    # How-To Use the service

    import predix.data.dbaas
    psql = predix.data.dbaas.PostgreSQL()
    rs = psql.execute('SELECT * FROM foo')
    for row in rs:
        print(str.join(',', row))

Find more examples in :ref:`dbaas-cookbook`.


Predix DBaaS API
................

.. automodule:: predix.data.dbaas
    :members:

Predix DBaaS Administration
...........................

.. automodule:: predix.admin.dbaas
    :members:

