
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

    wget https://download.redis.io/releases/redis-4.0.2.tar.gz
    tar xzf redis-4.0.2.tar.gz
    cd redis-4.0.2
    make
    cd src
    ./redis-cli -h $HOST -p $PORT -a $PASSWORD

You'll need to get the ``$HOST``, ``$PORT``, and ``$PASSWORD`` from your VCAP
environment variables.

.. _gotty-setup:

How-To Setup GoTTY
..................

GoTTY is an open-source, pre-built application you can run in the Predix Cloud
that provides a bash shell accessible via a web browser.

There are a few forks for the project, but follow the directions provided with
each for installing.

1. https://github.com/dmikusa-pivotal/cf-ex-gotty.git
2. https://github.com/gurjeet/gotty-cf-bash

In both cases, you will want to update the manifest.yml to properly secure the
environment with a username and password before pushing the app to Predix.
When you visit the app it'll behave like a ``bash`` prompt.

