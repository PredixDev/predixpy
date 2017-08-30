
Developer Guide
===============

This guide is to help contributors to the PredixPy project itself.

Dev Environment
---------------

After cloning the repository, you can install it in editable mode so that any
changes you make to the source are observable in your local dev environment
immediately::

   pip install -e

It is highly recommended to be using ``virtualenv`` to properly isolate your
dependencies.  There is also a docker image that may be helpful with Cloud
Foundry CLI installed::

   docker run -it --rm --volume=$(pwd):/home/app j12y/cf-ade-py

Quality Assurance
-----------------

To check coding style::

   python setup.py flake8

To check test coverage::

   python setup.py nosetests --with-coverage --cover-xml

Release Management
------------------

Running setuptools sdist will produce a file *dist/predix-x.y.z.tar.gz* which
can be useful.  It is not only the file needed to publish to PyPI, it can be
used in the **vendor/** folder used by the python_buildpack when deploying an
app to Cloud Foundry.

To build a distributable package with setuptools::

   python setup.py sdist


