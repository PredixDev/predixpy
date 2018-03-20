
import os

import predix.config
import predix.security.uaa
import predix.security.acs
import predix.admin.service


class AccessControl(object):
    """
    Access Control provides attribute based access control.
    """
    def __init__(self, name=None, plan_name=None, uaa=None, *args, **kwargs):
        super(AccessControl, self).__init__(*args, **kwargs)
        self.service_name = 'predix-acs'
        self.plan_name = plan_name or 'Free'
        self.use_class = predix.security.acs.AccessControl

        self.service = predix.admin.service.PredixService(self.service_name,
                self.plan_name, name=name, uaa=uaa)

    def _get_uri(self):
        """
        Will return the uri for an existing instance.
        """
        if not self.service.exists():
            logging.warning("Service does not yet exist.")

        return self.service.settings.data['uri']

    def _get_zone_id(self):
        """
        Will return the zone id for an existing instance.
        """
        if not self.service.exists():
            logging.warning("Service does not yet exist.")

        return self.service.settings.data['zone']['http-header-value']

    def exists(self):
        """
        Returns whether or not this service already exists.
        """
        return self.service.exists()

    def create(self):
        """
        Create an instance of the Access Control Service with the typical
        starting settings.
        """
        self.service.create()

        # Set environment variables for immediate use
        predix.config.set_env_value(self.use_class, 'uri', self._get_uri())
        predix.config.set_env_value(self.use_class, 'zone_id',
                self._get_zone_id())

    def grant_client(self, client_id):
        """
        Grant the given client id all the scopes and authorities
        needed to work with the access control service.
        """
        zone = self.service.settings.data['zone']['oauth-scope']

        scopes = ['openid', zone,
                  'acs.policies.read', 'acs.attributes.read',
                  'acs.policies.write', 'acs.attributes.write']

        authorities = ['uaa.resource', zone,
                  'acs.policies.read', 'acs.policies.write',
                  'acs.attributes.read', 'acs.attributes.write']

        self.service.uaa.uaac.update_client_grants(client_id, scope=scopes,
                authorities=authorities)

        return self.service.uaa.uaac.get_client(client_id)

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

        # Add environment variables
        uri = predix.config.get_env_key(self.use_class, 'uri')
        manifest.add_env_var(uri, self._get_uri())

        zone_id = predix.config.get_env_key(self.use_class, 'zone_id')
        manifest.add_env_var(zone_id, self._get_zone_id())

        manifest.write_manifest()
