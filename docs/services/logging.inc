
Logging
-------

The Logging Service is a Cloud Foundry log aggregator and management to aid
with application level debugging.  It can be used in combination with the ELK
stack for good results.  You can learn more from the `Logging`_ catalog page
and official documentation.

.. _Logging: https://www.predix.io/services/service.html?id=1184

Example
.......

Here is a simple demo of creating the service.

::

    # How-To Create the service

    import predix.admin.app
    admin = predix.admin.app.Manifest()
    admin.create_logging()

This should not be confused with Python's ``logging`` library but rather the
STDOUT and STDERR emitted by your application captured for later review like
you would see from the ``cf logs`` command.

Logging Administration
......................

.. automodule:: predix.admin.logstash
    :members:

