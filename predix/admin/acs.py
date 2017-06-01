
import os

import predix.app
import predix.security.uaa
import predix.admin.service


class AccessControl(object):
    """
    Access Control provides attribute based access control.
    """
    def __init__(self, name=None, uaa=None, *args, **kwargs):
        super(AccessControl, self).__init__(*args, **kwargs)
        self.service_name = 'predix-acs'
        self.plan_name = 'Free'
        self.service = predix.admin.service.PredixService(self.service_name,
                self.plan_name, name=name, uaa=uaa)

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
        os.environ['PREDIX_ACS_URI'] = self.service.settings.data['uri']
        os.environ['PREDIX_ACS_ZONE_ID'] = self.service.serttings.data['zone']['http-header-value']

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

    def add_to_manifest(self, manifest_path):
        """
        Add details to the manifest that applications using
        this service may need to consume.
        """
        manifest = predix.app.Manifest(manifest_path)

        # Add this service to list of services
        manifest.add_service(self.service.name)

        # Add environment variables
        manifest.add_env_var('PREDIX_ACS_URI',
                self.service.settings.data['uri'])
        manifest.add_env_var('PREDIX_ACS_ZONE_ID',
                self.service.settings.data['zone']['http-header-value'])

        manifest.write_manifest()
