
.. _cache-cookbook:

Predix Cache Recipes
--------------------

Recipes for working with Predix Python SDK and the Predix Cache service.

It is expected you used the SDK to create the service so that it is configured
by Manifest.

How-To Use the Redis CLI
........................

Predix Cache can only be used from within the Predix Cloud Foundry environment
so you won't be able to use Redis CLI running on your local machine.  As an
alternative, you can install an app into your space called GoTTY and then
install the Redis CLI.

First, see :ref:`gotty-setup` for instructions on setting up GoTTY.  Once
deployed to Predix Cloud, log into that environment and run the following
commands.

::

    ./redis-cli

This is an alias to a script that will lookup the host, port, and password from
your VCAP environment variables to launch ``redis-cli``.

See the official redis-cli docs for more details on how to use it once you
are connected.

How-To Build a Web App with Cache
.................................

See the following demo application for an example of a Flask app that uses
Predix Cache with PredixPy.

https://github.com/j12y/predixpy-flask-cache

