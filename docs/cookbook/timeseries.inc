
.. _timeseries-cookbook:

TimeSeries Recipes
-------------------

Recipes for working with Predix Python SDK and the Time Series service.

It is expected you used the SDK to create the service so that it is configured
by Manifest.

How-To Get List of Available Aggregations
.........................................

::

    import predix.app
    app = predix.app.Manifest()

    ts = app.get_timeseries()
    for aggregation in ts.get_aggregations():
        print(aggregation['name'])

How-To Simulate Time Series Data
................................

See the following example for a demonstration of generating random numbers
within a threshold for voltage readings across multiple sensors that can be
ingested in the Time Series service.

https://github.com/j12y/predixpy-timeseries-simulator

