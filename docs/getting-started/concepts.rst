
Concepts
--------

Manifest Apps
.............

The primary usage for the SDK is an application framework that persists
configuration details in the Cloud Foundry manifest.yml.  This is not strictly
necessary to make use of the SDK, but it is helpful as any environment
variables the SDK needs to interact with services are loaded.

To understand how the SDK works we'll explore its various behaviors while
logged into Cloud Foundry.

Creating Services
.................

The :ref:`quick-start` walked through setting up a brand new space from scratch
and creating services.

You may have noticed methods such as ``create_uaa()`` and
``create_timeseries()``.  The following diagram depicts the process flow for what
these **create** methods execute:

.. image:: images/predixpy-create.png

The SDK makes REST calls against the Cloud Foundry API endpoint to handle setup
operations.  The output is a manifest.yml written to disk with configuration
settings for accessing that service.

1. **create service** is similar to running ``cf create-service`` but has
   sensible defaults to get going quickly
2. **create service key** is similar to running ``cf create-service-key`` and
   avoids needing to create an initial app
3. **get service key** is similar to ``cf get-service-key`` to fetch details
   about the service such as a URI endpoint, Predix-Zone-Ids, etc.
4. **grant client** is similar to ``uaac`` in that it will use the service key
   details to setup the needed scopes and authorities for the client id used in
   the app
5. **write manifest** persists the environment variables in the manifest for
   later use

Consuming Services
..................

By using the SDK for Creating Services, consuming those services will be
straightforward and symmetrical across runtime environments.  See the following
diagram to represent the process flow: 

.. image:: images/predixpy-get.png

The previous step saw the creation of services and service keys which are
stored in the manifest.yml.  When we start consuming services, the
**manifest.yml** is read and all the environment variables loaded whether
running locally or in a Cloud Foundry envrionment.  This allows methods like
``get_timeseries()`` to know which time series instance to use.

For example, **PREDIX_SECURITY_UAA_URI** will contain the endpoint for your UAA
service instance and **PREDIX_DATA_TIMESERIES_INGEST_ZONE_ID** will have the
Predix-Zone-Id for ingesting into Predix Time Series.

If you don't want to use the SDK to create the services or persist the details
in your *manifest.yml* you can use any means you prefer to initialize these
envrionment variables.  The SDK will raise an error if you try to use
``predix.data.timeseries.TimeSeries`` but have not yet defined the UAA and
Predix Time Series environment variables.

Opinionated
...........

The ``predix.admin.app`` framework is opinionated in naming and choosing
service plans to use.  These will not work for all cases so you exchange some
flexibility for ease of use.

For new developers on Predix, reducing the cognitive overhead of making these
decisions may be an acceptable trade-off.  As you become more experienced, you
can override these with your own service names, different plans, or pass any
arbitrary parameters.

For example, instead of::

    app.create_timeseries()

you could view the source-code and call the underlying library directly::

    import predix.admin.app
    import predix.admin.timeseries

    # Create the service with new name and plan
    ts = predix.admin.timeseries.TimeSeries(name='my-timeseries', plan_name='Tiered')
    ts.create()

    # Use App Framework to persist environment and setup client grants
    admin = predix.admin.app.Manifest()
    ts.add_to_manifest(admin)
    ts.grant_client(admin.get_client_id())

Now that you have the basics under your belt, you can start using Predix
Python SDK to work with :ref:`service-index`.

