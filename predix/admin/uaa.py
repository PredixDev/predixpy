
import os
import uuid
import string
import random

import predix.config
import predix.admin.service

import predix.security.uaa


class UserAccountAuthentication(object):
    """
    User Account and Authentication Serice (UAA) provides user management
    for Cloud Foundry.

    A few helpful notes:
    - You must already be logged into a CF target environment
    - There can only be 10 instances of UAA within an org

    """
    def __init__(self, plan_name=None, name=None, *args, **kwargs):
        super(UserAccountAuthentication, self).__init__(*args, **kwargs)
        self.service_name = 'predix-uaa'
        self.plan_name = plan_name or 'Free'
        self.use_class = predix.security.uaa.UserAccountAuthentication

        self.service = predix.admin.service.CloudFoundryService(self.service_name,
                self.plan_name, name=name)
        self.is_admin = False

        # If UAA already created we can authenticate immediately
        if self.exists():
            self.authenticate()

    def _get_uri(self):
        """
        Returns the URI endpoint for this instance of the UAA service if it
        exists.
        """
        if not self.service.exists():
            logging.warning("Service does not yet exist.")

        return self.service.settings.data['uri']

    def exists(self):
        """
        Tests whether this given service already exists.
        """
        return self.service.exists()

    def create(self, secret):
        """
        Create a new instance of the UAA service.  Requires a
        secret password for the 'admin' user account.
        """
        parameters = {"adminClientSecret": secret}
        self.service.create(parameters=parameters)

        # Store URI into environment variable
        predix.config.set_env_value(self.use_class, 'uri', self._get_uri())

        # Once we create it login
        self.authenticate()

    def add_to_manifest(self, manifest):
        """
        Add useful details to the manifest about this service
        so that it can be used in an application.

        :param manifest: An predix.admin.app.Manifest object
            instance that manages reading/writing manifest config
            for a cloud foundry app.
        """
        # Add this service to list of services
        manifest.add_service(self.service.name)

        # Add environment variable to manifest
        varname = predix.config.set_env_value(self.use_class, 'uri',
                self._get_uri())
        manifest.add_env_var(varname, self._get_uri())

        manifest.write_manifest()

    def authenticate(self):
        """
        Authenticate into the UAA instance as the admin user.
        """
        # Make sure we've stored uri for use
        predix.config.set_env_value(self.use_class, 'uri', self._get_uri())

        self.uaac = predix.security.uaa.UserAccountAuthentication()
        self.uaac.authenticate('admin', self._get_admin_secret(),
                use_cache=False)
        self.is_admin = True

    def _create_id(self):
        """
        Return a GUID which can serve as a suitable client-id.
        """
        return str(uuid.uuid4())

    def _create_secret(self, length=12):
        """
        Use a cryptograhically-secure Pseudorandom number generator for picking
        a combination of letters, digits, and punctuation to be our secret.

        :param length: how long to make the secret (12 seems ok most of the time)

        """
        # Charset will have 64 +- characters
        charset = string.digits + string.ascii_letters + '+-'
        return "".join(random.SystemRandom().choice(charset) for _ in
                range(length))

    def create_client(self, client_id, client_secret):
        """
        Create a new client for use by applications.
        """
        assert self.is_admin, "Must authenticate() as admin to create client"
        return self.uaac.create_client(client_id, client_secret)

    def add_client_to_manifest(self, client_id, client_secret, manifest):
        """
        Add the client credentials to the specified manifest.
        """
        assert self.is_admin, "Must authenticate() as admin to create client"
        return self.uaac.add_client_to_manifest(client_id, client_secret,
                manifest)

    def _get_admin_secret(self):
        return self.service.settings.data['adminClientSecret']

    def _get_issuer_id(self):
        return self.service.settings.data['issuerId']
