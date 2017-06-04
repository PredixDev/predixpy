
import predix.app
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
        os.environ['PREDIX_IE_TRAFFIC_URI'] = self.service.settings.data['url']
        os.environ['PREDIX_IE_TRAFFIC_ZONE_ID'] = self.get_predix_zone_id()

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

    def add_to_manifest(self, manifest_path):
        """
        Add details to the manifest that applications using
        this service may need to consume.
        """
        manifest = predix.app.Manifest(manifest_path)

        # Add this service to list of services
        manifest.add_service(self.service.name)

        # Add environment variables
        manifest.add_env_var('PREDIX_IE_TRAFFIC_URI',
                self.service.settings.data['url'])
        manifest.add_env_var('PREDIX_IE_TRAFFIC_ZONE_ID',
                self.get_predix_zone_id())

        manifest.write_manifest()
