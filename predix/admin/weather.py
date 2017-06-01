
import os

import predix.app
import predix.admin.service


class WeatherForecast(object):
    def __init__(self, plan_name=None, name=None, uaa=None, *args, **kwargs):
        super(WeatherForecast, self).__init__(*args, **kwargs)
        self.service_name = 'us-weather-forecast'
        self.plan_name = plan_name or 'Beta'
        self.service = predix.admin.service.PredixService(self.service_name,
                self.plan_name, name=name, uaa=uaa)

    def exists(self):
        """
        Returns whether or not this service already exists.
        """
        return self.service.exists()

    def create(self):
        """
        Create an instance of the US Weather Forecast Service with
        typical starting settings.
        """
        self.service.create()

        zone = self.service.settings.data['zone']['http-header-value']
        os.environ['PREDIX_WEATHER_ZONE_ID'] = zone
        uri = self.service.settings.data['uri']
        os.environ['PREDIX_WEATHER_URI'] = uri

    def add_to_manifest(self, manifest_path):
        manifest = predix.app.Manifest(manifest_path)

        # Add this service to list of services
        manifest.add_service(self.service.name)

        # Add environment variables
        manifest.add_env_var('PREDIX_WEATHER_ZONE_ID',
                self.service.settings.data['zone']['http-header-value'])
        manifest.add_env_var('PREDIX_WEATHER_URI',
                self.service.settings.data['uri'])

        manifest.write_manifest()

    def get_oauth_scope(self):
        return self.service.settings.data['zone']['oauth-scope']

    def grant_client(self, client_id):
        """
        Grant the given client with any scopes or authorities
        needed to use this service.
        """
        scopes = ['openid']
        authorities = ['uaa.resource']

        scopes.append(self.get_oauth_scope())
        authorities.append(self.get_oauth_scope())

        self.service.uaa.uaac.update_client_grants(client_id, scope=scopes,
                authorities=authorities)

        return self.service.uaa.uaac.get_client(client_id)
