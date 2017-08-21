
# PredixPy

**This SDK is still pre-release / alpha under development.**

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

There are two modes of operations that PredixPy helps to solve.

1. You are administering a cloud foundry space and want to automate the
   creation and configuration of services.
2. You are using service instances from cloud foundry and running your app
   locally or on cloud foundry.

There are two separate application frameworks for managing this process that
revolve around writing or reading configuration details to the manifest.yml

## Administration Mode

When you have done a `cf login` to a Cloud Foundry endpoint you can begin
creating services in Python.

```
# The manifest can be used for managing your work
import predix.admin.app
app = predix.admin.app.Manifest()

# Create a UAA service instance as most services require it, and a client
# that your application can use for accessingn services.
app.create_uaa('admin-secret')
app.create_client('client-id', 'client-secret')

# Create a Time Series service instance once UAA is created.
app.create_timeseries()
```

## Application Mode

Once your space has been configured like the above example, you can use
PredixPy to work with the services in your applications.

```
# If not in a Cloud Foundry deployed environment and testing locally,
# you can use this manifest utility to load environment variables
# into your process.

import predix.app
app = predix.app.Manifest()
ts = app.get_timeseries()
ts.send('TEMP', 70.1)
print(ts.get_values('TEMP'))
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

[![Analytics](https://ga-beacon.appspot.com/UA-82773213-1/predix-sdks/readme?pixel)](https://github.com/PredixDev)


---
[catalog]: https://www.predix.io/catalog/services

