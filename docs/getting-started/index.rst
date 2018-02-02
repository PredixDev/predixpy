
Getting Started
===============

The following services are supported.

- User Account and Authentication (UAA)
- Predix Access Control (ACS)
- Predix Asset
- Predix Time Series
- Blob Store
- Logging
- ... for more see :ref:`service-index` section

.. _quick-start:

Installation
------------

Install it from PyPI::

   pip install predix

If that isn't working for you, we highly recommend `The Hitchiker's Guide to
Properly Installing Python`_ to learn about installing ``python``, ``pip``, and
``virtualenv`` for your environment.  For industrial environments, you may also
need to learn how to set your proxies.

.. _The Hitchiker's Guide to Properly Installing Python: http://docs.python-guide.org/en/latest/starting/installation/

If you run into trouble installing check out the :ref:`installation-cookbook` for
more help.

First Steps
-----------

The Predix Python SDK helps you (1) create services in your space, (2) configure your
app to work with those services, and (3) communicate with those services.

.. important::

   In order to use the Predix Python SDK to communicate with services it must
   be configured to know how to find the ones provisioned in your space.  This
   is accomplished with environment variables.  For example,
   **PREDIX_SECURITY_UAA_URI** is expected to be set for your UAA instance.

   Fortunately, the SDK can help with that.

Before we begin, we need to log into a Predix API endpoint and create a space
for us to experiment in.

::

    cf login
    cf create-space predixpy-demo
    cf target -s predixpy-demo

It is often helpful to be able to completely reproduce a space with all of the
services and initial data for it to work -- a dev, qa, and prod environment for
example.  By using the Python SDK we can generate a script that will do this
replication for us.

Let's start by initializing some services using the ``predix.admin.app``
library in a file called ``initialize-space.py``.

::

    #!/bin/env python

    import predix.admin.app
    admin = predix.admin.app.Manifest()

    admin.create_uaa('admin-secret')
    admin.create_client('client-id', 'client-secret')

    admin.create_timeseries()

This simple admin script would be run only *once* at the beginning of a project to:

- create an instance of UAA
- create a client for your application
- create an instance of Predix Time Series
- grant the client the authorities and scopes for Predix Time Series
- stores environment variables in manifest.yml so you can work both locally or the cloud

Run the script and you should be able to see services in your space such as
**predix-timeseries** and **predix-uaa**.

::

    python initialize-space.py
    cf services

.. warning::

   You don't want to deploy admin scripts to a Cloud Foundry environment.
   Their purpose is to set up your environment in the first place.

   You should also avoid checking your **manifest.yml** into a public
   revision control system unless you've encrypted your secrets.

Now that you've created services and configured your manifest.yml you can
begin sending data to these services.  Create a new script called ``app.py`` to
do the following:

::

    #!/bin/env python

    import predix.app

    app = predix.app.Manifest()
    ts = app.get_timeseries()

    ts.send('TEMP', 70.1)
    for val in ts.get_values('TEMP'):
        print(val)

Once you understand how the Predix Python SDK works this simple script is all
you need to send data to Predix Time Series.  The SDK takes care of many details
for you:

- generating a uaa token
- constructing request headers and the json body
- establishing a websocket connection
- making the service calls
- handling failures and retries

This simple demonstration was for Time Series but the basic pattern follows for
any of the services currently supported by the SDK with more on the way.

.. include:: concepts.rst

Building Apps
-------------

The SDK is a client library for service calls and its purpose is to help
developers build many different types of apps.

- CLI tools
- Data engineering tasks
- Standalone GUIs
- Web applications with Flask, Django, Turbogears, etc.
- Microservices

See the `Predix Volcano App`_ for a full demonstration of the SDK used in a
Python Flask App.

.. _Predix Volcano App: https://github.com/PredixDev/predix-volcano-app

