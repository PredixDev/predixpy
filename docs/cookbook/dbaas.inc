
.. _dbaas-cookbook:

Predix DBaaS Recipes
--------------------

Recipes for working with Predix Python SDK and the Predix PostgreSQL service.

It is expected you used the SDK to create the service so that it is configured
by Manifest.

How-To Use the PostgreSQL CLI
.............................

PostgreSQL can only be used from within the Predix Cloud Foundry environment so
you won't be able to use ``pgsql`` running on your local machine.  As an
alternative, you can install an app into your space called GoTTY and then
install the Redix CLI.

First, see :ref:`gotty-setup` for instructions on setting up GoTTY.  Once
deployed to Predix Cloud, log into that environment and run the following
commands.

::

    psql

This is an alias to a script that will lookup the host, port, username, and
password from your VCAP environment variables to launch ``psql``.

See the official psql docs for more details on how to use it once you are
connected.


