
.. _installation-cookbook:

Installation Recipes
--------------------

Recipes for installation issues with Predix Python SDK.

How-To Install the Python SDK
.............................

If you ran into issues installing the SDK with ``pip install predix`` there may
be a few things that could have gone wrong.

1. Python Version
2. Python Installation
3. Proxies

**Python Version**

There are a few minor issues before version 0.1.0 that prevent the SDK from
working in a Python 3.x environment.  You'll either need to work with Python
2.7 or watch the repository until 0.1.0 is released.

**Python Installation**

Certain Python versions don't have ``pip`` installed or you may be trying to
use a version of ``python`` that is on your system by default.

You should have Python 2.7.10+ and pip 9.0.1+ and write permissions for the
Python packages.  It is also highly recommended to use Virtual Environments.

If you need help with these, check out the `Hitchiker's Guide to
Python`_ or `Python docs`_ for details.

.. _Python docs: https://wiki.python.org/moin/BeginnersGuide
.. _Hitchiker's Guide to Python: http://docs.python-guide.org/en/latest/starting/installation/

**Proxies**

If you are in an industrial environment you may need to set proxies in your
environment.  The Python interpreter will pull these variables in at runtime so
there shouldn't be too much you need to do.

You can use the ``env`` section of your ``manifest.yml`` if you want to limit
the scope of those environments to ``predix.app``.

There is a good Predix `Proxies` guide you may want to review.

.. _Proxies: https://www.predix.io/resources/tutorials/tutorial-details.html?tutorial_id=1565

How-To Learn the SDK
....................

The documentation on this site is here to help you, but sometimes you need to
learn by doing.  Run ``pip install ipython`` to use an interactive python shell
where you can tab complete and use ``?`` to lookup docstrings for methods.

.. parsed-literal::

    In [6]: asset?
    Type:        Asset
    String form: <predix.data.asset.Asset object at 0x10adcdc10>
    File:        ~/w/predixpy/j12y/predixpy/predix/data/asset.py
    Docstring:
    Client library for working with the Predix Asset Service.  For more details
    on use of the service please see official docs:
    https://www.predix.io/services/service.html?id=1171

How-To Run a Dockerized Dev Environment
.......................................

If you already use Docker, you may find it easy to start up a container that
has the ``cf`` cli pre-installed and ready to use.

See the following project for more details on this Docker-based Application
Development Environment:

https://github.com/j12y/cf-ade

