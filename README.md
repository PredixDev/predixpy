
# PredixPy

The Predix Python SDK aims to help accelerate application development with
client libraries for commonly used Predix Platform Services.  This framework
provides helper methods and classes.

You can find out more about services in the [Predix Service Catalog][catalog].

## Installation

To start using the SDK downloaded from PyPI:

```
$ pip install predix
```

If you want to install from source, see developer section below.

# Basic Usage

## Administration

When you have done a `cf login` to a Cloud Foundry endpoint you can begin
creating services in Python.

```
# Create a UAA service instance as most services require it
# and create a client for your application
import predix.admin.uaa
uaa = predix.admin.uaa.UserAccountAuthentication()
uaa.create('admin-secret')

# Cloud Foundry applications require client authorization and a
# manifest helps for when you `cf push`.
uaa.create_client('my-client', 'my-client-secret')
uaa.add_to_manifest('./manifest.yml')
uaa.add_client_to_manifest('my-client', 'my-client-secret', './manifest.yml')

# Create a Time Series service instance
import predix.admin.timeseries
ts = predix.admin.timeseries.TimeSeries()
ts.create()

# Let client use this service
ts.grant_client('my-client')
ts.add_to_manifest('./manifest.yml')

```

## Applications

Once your space has been configured, you can use PredixPy to work with
the services in your applications.

```
# If not in a Cloud Foundry deployed environment and testing locally,
# you can use this manifest utility to load environment variables
# into your process.

import predix.app
manifest = predix.app.Manifest('./manifest.yml')

# Start using the services

import predix.data.timeseries

ts = predix.data.timeseries.TimeSeries()
ts.send('test', 12)
print(ts.get_values('test'))
```

# Developing PredixPy

## Setup Environment

To install into your environment for use in editable mode:

```
$ pip install -e .
```

Recommend using `virtualenv` or `venv`.  If you prefer to use a docker
environment there is one with cloud foundry pre-installed:

```
$ docker run -it --rm --volume=$(pwd):/home/app j12y/cf-ade-py
```

## Quality

To check coding style:
```
$ python setup.py flake8
```

To check test coverage:
```
$ python setup.py nosetests --with-coverage --cover-xml
```

## Distribution

Running setuptools sdist will produce a file `dist/predix-x.y.z.tar.gz` which
can be useful.  It is not only the file needed to publish to PyPI, it can be
used in the **vendor/** folder used by the python_buildpack when deploying an
app to Cloud Foundry.
```
$ python setup.py sdist
```



---
[catalog]: https://www.predix.io/catalog/services

