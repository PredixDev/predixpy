
Time Series
-----------

The Time Series Service is a persistent store for a series of data points over
time such as sensor data.

You can learn more from the `Time Series`_ catalog page and official
documentation.

.. _Time Series: https://www.predix.io/services/service.html?id=1177

Example
.......

Here is a simple demo to create a time series instance and a basic use example
of sending data.

::

    # How-To Create the service
    # IMPORTANT: You must have already configured UAA and client

    import predix.admin.app
    app = predix.admin.app.Manifest()
    app.create_timeseries()

::

    # How-To Use the Service

    import predix.app
    app = predix.app.Manifest()
    timeseries = app.get_timeseries()
    timeseries.send('TEMP', 72)

Find more examples with :ref:`timeseries-cookbook`.

Tags and Values
...............

The minimum you need for adding data to Predix Time Series is a **tag** and a
**value**.  The value will typically be a numerical value and the tag a simple
string label for the type of data.

Predix Time Series also requires

Quality and Attributes
......................

Every data point must also have a quality designation.  By default the SDK will
assign it as UNCERTAIN and there are constants for the various values.

Attributes are also optional, but any Python dictionary with simple data types
will be marshalled into Predix Time Series.  You may want to include things
like URIs for the assets or sensors being observed.

Time Series API
...............

.. automodule:: predix.data.timeseries
    :members:

Time Series Administration
..........................

.. automodule:: predix.admin.timeseries
    :members:
