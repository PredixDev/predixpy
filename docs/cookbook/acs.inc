
.. _acs-cookbook:

ACS Recipes
-----------

Recipes for working with Predix Python SDK and the ACS service.

It is expected you used the SDK to create the service so that it is configured
by Manifest.

How-To Add a Policy and Test Access
....................................

If you followed the basic example from the :ref:`acs-service` you may have
subjects and resources stored.  Now you want to create a policy to test if a
subject can perform an action on a resource.

::

    resource = {'uriTemplate': '/asset'}
    subject = {'name': 'devangelist', 'attributes': [{"issuer": "default", "name": "role"}]}
    condition = "match.single(subject.attributes('default', 'role'), 'devangelist')"

    acs.add_policy('any_devangelist', 'GET', resource, subject, condition)

    print(acs.is_allowed('/user/j12y', 'GET', '/asset/12'))
    print(acs.is_allowed('/user/jflannery', 'GET', '/asset/12'))
  
This example compares the given subjects to see if their role allows access or
not.


