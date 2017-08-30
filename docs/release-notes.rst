
Release Notes
=============

0.0.9
-----

**Logstash**

Create instances of logstash logging service.  You will still need to push an
app such as `kibana-me-logs`_.

.. _kibana-me-logs: https://github.com/cloudfoundry-community/kibana-me-logs] manually.

For example::

    import predix.admin.app
    app = predix.admin.app.Manifest()
    app.create_logstash()


