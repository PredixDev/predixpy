
.. _references-cookbook:

Reference Recipes
-----------------

A collection of resources and reference applications where you can find more
about using Python on Predix or use the Predix SDK for multiple services.

How-To Install the Predix Volcano App
.....................................

The Predix Volcano App demonstrates use of UAA, Predix Asset and Predix Time
Series in a Python Flask application.  The following repository has
instructions for how to setup the services, ingest data, deploy, and monitor
this sort of public application using the Predix Python SDK.

https://github.com/PredixDev/predix-volcano-app/

How-To Run a Flask App with Python 3.x
......................................

The trick is setting up a ``runtime.txt`` that the Cloud Foundry Python
Buildpack will identify to specify a different Python runtime envrionment.

Complete reference project:
https://github.com/j12y/predix-py3-flask

How-To Run TensorFlow in Cloud Foundry
......................................

Architecturally you may not want to do this, but you can find a demonstration
of running a simple TensorFlow operation in Cloud Foundry with this repository.

Complete reference project:
https://github.com/j12y/predix-tensorflow-example

