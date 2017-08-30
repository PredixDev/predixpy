
Getting Started
===============

The following services are supported for **Python 2.7.x**.  Verification of
compatibility with **Python 3.6.x** is on the near-term roadmap.

- User Account and Authentication (UAA)
- Predix Access Control (ACS)
- Predix Asset
- Predix Time Series
- Blob Store
- Logging
- ... for more see :ref:`service-index` section

Summary
-------

Let's start with a simple example script that you could run in your local
development environment and space.

::

    import predix.app

    app = predix.app.Manifest()
    ts = app.get_timeseries()

    ts.send('TEMP', 70.1)
    print(ts.get_values('TEMP'))

Once you understand how the Predix Python SDK works this simple script is all
you need to send data to Predix Time Series.  The SDK takes care of the details
for you:

- establishing a websocket connection
- generating a uaa token
- constructing the json
- making web service calls
- handling failures and retries

.. important::

   This only works if you have the services provisioned in your space and
   environment variables defined.  

Fortunately, the Predix Python SDK helps you with that as well.

::

    import predix.admin.app
    app = predix.admin.app.Manifest()

    app.create_uaa('admin-secret')
    app.create_client('client-id', 'client-secret')

    app.create_timeseries()
    
This admin script would be run once during setup to:

- create an instance of UAA
- create a client for your application
- grants the client the authorities and scopes
- creates an instance of timeseries
- caches environment variables so you can work locally or the cloud

.. warning::

   You don't want to run admin scripts in a Cloud Foundry environment.  Their
   purpose is to set up your environment in the first place.

Manifest Application Framework
------------------------------

The SDK has introduced an application framework that persists configuration
details in the cloud foundry manifest.yml.  This is not strictly necessary, but
it helps with setting the environment variables the SDK needs to interact with
services.

To understand how the SDK works let's start with an empty space while logged
into Cloud Foundry.

::

    cf login
    cf create-space predixpy
    cf target -s predixpy

Creating Services
.................

When you run the setup script and ``create()`` methods the process flow looks
like this:

.. image:: images/predixpy-create.png

The SDK makes REST calls against the Cloud Foundry API endpoint to handle setup
operations for us.  The output is a manifest.yml written to disk and a properly
configured service.

The steps include:

1. Create Service: for example ``create_timeseries()`` creates an instance of
   Predix Time Series.
2. Create Service Key: this is only needed for some services, but the service
   key allows us to access details around the provisioned service instance
3. Get Service Key: without pushing any apps, the service key provides us the
   details such as URI endpoints and Predix-Zone-Ids needed to use the service.
4. Grant Client: when needed will configure the scopes and authorities for the
   client being used by the app.
5. Write Manifest: take these details and encrypt them in the manifest.yml for
   easy access by your application as environment variables.

Consuming Services
..................

If you are using the SDK's Manifest Application Framework to ``create()``
services, consuming those services will be straightforward.  

.. image:: images/predixpy-get.png

Since all the service key details were stored in the manifest.yml, the
``get()`` methods will read and load the env variables into your local
operating system environment.  If your runtime is in Cloud Foundry, these
variables can be pulled from VCAP variables instead.


For example, PREDIX_SECURITY_UAA_URI will contain the endpoint for your UAA
service instance and PREDIX_DATA_TIMESERIES_INGEST_ZONE_ID will have the
Predix-Zone-Id for ingesting into Predix Time Series.

If you don't want to use the SDK to create the services or persist the details
in your manifest.yml, you can replace that portion of the SDK so long as you
define the required environment variables through another means.

Opinionated
...........

The SDK has some opinions and default values for things.  If you use the
Manifest Application Framework to create services you exchange some flexibility
for ease of use.

- Naming convention for your services
- Plans for your services

For new developers on Predix, reducing the cognitive overhead of making these
decisions may be an acceptable trade-off.  As you become more experienced, you
can override these with your own service names, different plans, or pass any
arbitrary parameters.

For example, instead of::

    app.create_timeseries()

you could view the source-code and call the underlying libraries directly::

    import predix.admin.timeseries

    app = predix.admin.app.Manifest()

    ts = predix.admin.timeseries.TimeSeries(name='my-timeseries', plan_name='Tiered')
    ts.add_to_manifest(app)

App Development
---------------

The SDK allows you to develop many types of applications.  It is just a client
library for service calls.

- CLI tools
- Data engineering tasks
- Standalone GUIs
- Web applications with Flask, Django, Turbogears, etc.

See the `Predix Volcano App`_ for a full demonstration of the SDK used in a
Python Flask App.

.. _Predix Volcano App: https://github.com/PredixDev/predix-volcano-app

.. note::

   Some services are limited to only running in a Cloud Foundry environment
   (PostgreSQL, Blob Store) but others can be reached from anywhere
   connectivity is available (Time Series, Asset) on the edge or your
   workstation.

Now that you have the basics under your belt, you can start using Predix
Services.
