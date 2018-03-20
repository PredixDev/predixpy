
import os

import predix.security.uaa
import predix.admin.service

class ParkingPlanning(object):
    """
    Optimize operations and planning with vehicle parking data.
    """
    def __init__(self, name=None, uaa=None, *args, **kwargs):
        super(ParkingPlanning, self).__init__(*args, **kwargs)
        self.service_name = 'ie-traffic'
        self.plan_name = 'Beta'
        self.service = predix.admin.service.PredixService(self.service_name,
                self.plan_name, name=name, uaa=uaa)

    def exists(self):
        """
        Returns whether or not this service already exists.
        """
        return self.service.exists()

    def create(self):
        """
        Create an instance of the Parking Planning Service with the
        typical starting settings.
        """
        self.service.create()
        os.environ[self.__module__ + '.uri'] = self.service.settings.data['url']
        os.environ[self.__module__ + '.zone_id'] = self.get_predix_zone_id()

    def grant_client(self, client_id):
        """
        Grant the given client id all the scopes and authorities
        needed to work with the parking planning service.
        """
        zone = self.get_oauth_scope()
        scopes = ['openid', zone]
        authorities = ['uaa.resource', zone]

        self.service.uaa.uaac.update_client_grants(client_id, scope=scopes,
                authorities=authorities)

        return self.service.uaa.uaac.get_client(client_id)

    def get_oauth_scope(self):
        """
        Simply returns the configured service oauth scope needed
        in client uaa grants.
        """
        return self.service.settings.data['zone']['oauth-scope']

    def get_predix_zone_id(self):
        """
        Simply returns the configured service predix zone id.
        """
        return self.service.settings.data['zone']['http-header-value']

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
        manifest.add_env_var(self.__module__ + '.uri',
                self.service.settings.data['url'])
        manifest.add_env_var(self.__module__ + '.zone_id',
                self.get_predix_zone_id())

        manifest.write_manifest()
