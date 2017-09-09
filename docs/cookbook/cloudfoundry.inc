
.. _cloudfoundry-cookbook:

Cloud Foundry Recipes
---------------------

Recipes for working effectively with a Cloud Foundry environment.

How-To Deploy an App
....................

The Python SDK does not provide this feature.  You should just use ``cf push``.

How-To Authenticate to Cloud Foundry
....................................

The Python SDK does not provide this feature.  You should just use ``cf
login``.

How-To Specify a Python Buildpack
.................................

You can run ``cf buildpacks`` to see the version of the buildpack installed in
Predix, but sometimes you want to use a newer version of the Python buildpack
for a new feature or bug fix.  You can do so by specifying ``-b
https://github.com/cloudfoundry/python-buildpack.git#v1.5.20`` on the command
line or put it in your manifest.yml.

See a post on the Predix Developer Forums for more details:

https://forum.predix.io/articles/24714/how-to-specify-a-python-buildpack.html

How-To Include Private Python Libraries in CF
.............................................

If you have Python libraries in a private source code repository or cannot
publish to public indexes like PyPI you may not know how to include them in
your Cloud Foundry App.

If you add a folder called ``vendor`` to your project, the Python Buildpack
will presume you do not have Internet access to any dependencies and will look
for any dependencies in that folder.

By running ``pip download -r requirements.txt -d vendor`` you can pull down all
the dependencies for your app and then run ``python setup.py sdist`` to
generate a tar.gz for your own library to include.

These will be packaged and deployed with your Cloud Foundry Droplet.

See a post on the Predix Developer Forums for more details:
https://forum.predix.io/articles/24733/how-to-include-your-own-private-python-libraries-i.html

How-To Specify a different version of Python
............................................

If you add a ``runtime.txt`` file in the same directory as your manifest.yml
you can specify a single line in the file to signify the version.

For example:

..

    python-3.6.1

or

..

    python-2.7.13

Only specific versions supported by each python_buildpack release so check the
release notes for details.

https://github.com/cloudfoundry/python-buildpack/releases/tag/v1.5.20

See a post on the Predix Developer Forums for more details:
https://forum.predix.io/articles/24718/how-to-specify-a-python-version-for-your-app.html

