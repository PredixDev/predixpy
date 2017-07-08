
import os

import predix.config
import predix.admin.service
import predix.data.weather


class WeatherForecast(object):
    def __init__(self, plan_name=None, name=None, uaa=None, *args, **kwargs):
        super(WeatherForecast, self).__init__(*args, **kwargs)
        self.service_name = 'us-weather-forecast'
        self.plan_name = plan_name or 'Beta'
        self.use_class = predix.data.weather.WeatherForecast

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

        # Set env vars for immediate use
        zone_id = predix.config.get_env_key(self.use_class, 'zone_id')
        zone = self.service.settings.data['zone']['http-header-value']
        os.environ[zone_id] = zone

        uri = predix.config.get_env_key(self.use_class, 'uri')
        os.environ[uri] = self.service.settings.data['uri']

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
        zone_id = predix.config.get_env_key(self.use_class, 'zone_id')
        manifest.add_env_var(zone_id,
                self.service.settings.data['zone']['http-header-value'])

        uri = predix.config.get_env_key(self.use_class, 'uri')
        manifest.add_env_var(uri, self.service.settings.data['uri'])

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
