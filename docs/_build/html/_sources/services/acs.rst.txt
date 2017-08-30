
Access Control
--------------

The Access Control Service, known as ACS, is a fine-grained access control
system common in complex dynamic industrial settings.  You can learn more about
it from the `ACS`_ catalog page.

.. _ACS: https://www.predix.io/services/service.html?id=1180

Example
.......

Here is a simple demo to create an acs instance and a basic use example of
evaluating access policy.

    import predix.admin.app
    app = predix.admin.app.Manifest()
    app.create_uaa('admin-secret')
    app.create_client('my-client', 'my-client-secret')
    app.create_acs()

    import predix.app
    app = predix.app.Manifest()
    acs = app.get_acs()
    acs.add_subject('/user/j12y', {'username': 'j12y', 'role': 'devangelist'})
    acs.add_subject('/user/jflannery', {'username': 'jflannery', 'role': 'ceo'})
    acs.add_resource('/asset/12', {'manufacturer': 'GE Digital'})

    resource = {'uriTemplate': '/asset'}
    subject = {'name': 'devangelist', 'attributes': [{"issuer": "default", "name": "role"}]}
    condition = "match.single(subject.attributes('default', 'role'), 'devangelist')"

    acs.add_policy('any_devangelist', 'GET', resource, subject, condition)

    print(acs.is_allowed('/user/j12y', 'GET', '/asset/12'))
    print(acs.is_allowed('/user/jflannery', 'GET', '/asset/12'))

Authorization
.............

*I have lots of data in my system, for any specific piece of data is a given
subject allowed to operate on it?*  

ACS uses attributes assigned to subjects and resources to determine
authorization for a resource.  It does not handle authentication, only whether
access should be granted to read, write, delete, etc. a resource by a given
subject.

What is a **subject**?  A subject could be a user or a machine.  It has
properties and attributes we know about it and can be assigned a unique uri to
identify it.

What is a **resource**?  A resource could be a service, a piece of data, or an
asset.  It too has properties like subjects do and has a unique uri.

If you consider well known commercial systems like Box, Dropbox, or Google
Drive -- subjects are the users that have logged in and the resources are the
shared documents that the subject may be able to read or write.

Policies
........

ACS maintains its own cache of subject and resource attributes in order to
evaluate policies.  Policies define a specification for what resources and
subjects are impacted and what condition must be met.

The condition is a groovy expression.

Where UAA provides coarse-grained policies for whether a service is available
to a client at all, ACS helps provide the fine-grained per-data level of
flexibility that can be handled in a scalable way for sophistated permission
schemes needed in complex organizational structures.

API
...

.. automodule:: predix.security.acs
    :members:

Administration
..............

.. automodule:: predix.admin.acs
    :members:

