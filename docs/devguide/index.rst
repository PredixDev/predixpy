
Contributor Guide
=================

This guide is to help contributors to the PredixPy project itself.

- Install Homebrew - https://brew.sh
- Install CF CLI - https://docs.cloudfoundry.org/cf-cli/install-go-cli.html
- Install Python - http://docs.python-guide.org/en/latest/starting/install/osx/#install-osx

How-To Setup Your Dev Environment
---------------------------------

After cloning this repository it is highly recommended to be using
``virtualenv`` or similar tooling to isolate your dependencies.  This will also
make doing development and switching between Python 2.7 and Python 3.x easier.

In your environment you can run:

::

    pip install -e

This will install the library to site packages with a symlink back to the
GitHub repository.  This will allow any changes you make to have an immediate
effect on your environment.

How-To Run Tests
----------------

To run unit tests and verify everything is still passing you can run

::

    python setup.py test

You can also increase verbosity for more details

::

    python setup.py nosetests --verbosity=2

How-To Check Coding Style
-------------------------

For testing PEP-8 and style guide against the codebase::

   python setup.py flake8

How-To Check Test Coverage
--------------------------

To check test coverage::

   python setup.py nosetests --with-coverage --cover-xml

How-To Package Dependency
-------------------------

Using seutptools you can generate *dist/predix-x.y.z.tar.gz* which can be used
to publish to PyPI with ``twine`` or used in a Cloud Foundry ``vendor``
directory.

To build a distributable package with setuptools::

   python setup.py sdist

The version comes from incrementing the value in *setup.py*.

