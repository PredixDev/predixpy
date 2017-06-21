
import os
import yaml


class Manifest(object):
    """
    Cloud Foundry utilizes a MANIFEST.yml file as the source
    of application configuration.  As we setup services and
    run our applications the manifest is a place to store
    important configuration details.
    """
    def __init__(self, manifest_path, app_name='my-predix-app'):
        self.manifest_path = os.path.expanduser(manifest_path)
        self.app_name = app_name

        # App may have a client
        self.client_id = None
        self.client_secret = None

        # Read or Generate a manifest file
        if os.path.exists(self.manifest_path):
            manifest = self.read_manifest()
        else:
            manifest = self.create_manifest()

        # Probably always want manifest loaded into environment
        self.set_os_environ()

    def read_manifest(self):
        """
        Read an existing manifest.
        """
        with open(self.manifest_path, 'r') as input_file:
            self.manifest = yaml.safe_load(input_file)
            if 'env' not in self.manifest:
                self.manifest['env'] = {}
            if 'services' not in self.manifest:
                self.manifest['services'] = []

            input_file.close()

    def create_manifest(self):
        """
        Create a new manifest and write it to
        disk.
        """
        self.manifest = {}
        self.manifest['applications'] = [{'name': self.app_name}]
        self.manifest['services'] = []
        self.manifest['env'] = {}

        self.write_manifest()

    def write_manifest(self):
        """
        Write manifest to disk.
        """
        with open(self.manifest_path, 'w') as output_file:
            yaml.safe_dump(self.manifest, output_file,
                    default_flow_style=False, explicit_start=True)
            output_file.close()

    def add_env_var(self, key, value):
        """
        Add the given key / value as another environment
        variable.
        """
        self.manifest['env'][key] = value

    def add_service(self, service_name):
        """
        Add the given service to the manifest.
        """
        if service_name not in self.manifest['services']:
            self.manifest['services'].append(service_name)

    def set_os_environ(self):
        """
        Will load any environment variables found in the
        manifest file into the current process for use
        by applications.

        When apps run in cloud foundry this would happen
        automatically.
        """
        for key in self.manifest['env'].keys():
            os.environ[key] = self.manifest['env'][key]

    def get_client_id(self):
        """
        Return the client id that should have all the
        needed scopes and authorities for the services
        in this manifest.
        """
        key = 'predix.security.uaa.client_id'
        if key not in self.manifest['env']:
            raise ValueError("%s undefined in manifest." % key)

        self.client_id = self.manifest['env'][key]
        return self.client_id

    def get_client_secret(self):
        """
        Return the client secret that should correspond with
        the client id.
        """
        key = 'predix.security.uaa.client_secret'
        if key not in self.manifest['env']:
            raise ValueError("%s must be added to manifest." % key)

        self.client_secret = self.manifest['env'][key]
        return self.client_secret

    def create_timeseries(self):
        """
        Creates an instance of the Time Series Service.
        """
        import predix.admin.timeseries
        ts = predix.admin.timeseries.TimeSeries()
        ts.create()

        client_id = self.get_client_id()
        if client_id:
            ts.grant_client(client_id)

        ts.add_to_manifest(self.manifest_path)
        return ts

    def get_timeseries(self, *args, **kwargs):
        """
        Returns an instance of the Time Series Service.
        """
        import predix.data.timeseries
        ts = predix.data.timeseries.TimeSeries(*args, **kwargs)
        return ts

    def create_asset(self):
        """
        Creates an instance of the Asset Service.
        """
        import predix.admin.asset
        asset = predix.admin.asset.Asset()
        asset.create()

        client_id = self.get_client_id()
        if client_id:
            asset.grant_client(client_id)

        asset.add_to_manifest(self.manifest_path)
        return asset

    def get_asset(self):
        """
        Returns an instance of the Asset Service.
        """
        import predix.data.asset
        asset = predix.data.asset.Asset()
        return asset

    def create_uaa(self, admin_secret):
        """
        Creates an instance of UAA Service.
        """
        import predix.admin.uaa
        uaa = predix.admin.uaa.UserAccountAuthentication()
        if not uaa.exists():
            uaa.create(admin_secret)
            uaa.add_to_manifest(self.manifest_path)
        return uaa

    def create_client(self, client_id, client_secret):
        """
        Create a client and add it to the manifest.
        """
        import predix.admin.uaa
        uaa = predix.admin.uaa.UserAccountAuthentication()
        uaa.create_client(client_id, client_secret)
        uaa.add_client_to_manifest(client_id, client_secret,
                self.manifest_path)

    def get_uaa(self):
        """
        Returns an insstance of the UAA Service.
        """
        import predix.security.uaa
        uaa = predix.security.uaa.UserAccountAuthentication()
        return uaa

    def create_acs(self):
        """
        Creates an instance of the Asset Service.
        """
        import predix.admin.acs
        acs = predix.admin.acs.AccessControl()
        acs.create()

        client_id = self.get_client_id()
        if client_id:
            acs.grant_client(client_id)

        acs.grant_client(client_id)
        acs.add_to_manifest(self.manifest_path)
        return acs

    def get_acs(self):
        """
        Returns an instance of the Asset Control Service.
        """
        import predix.security.acs
        acs = predix.security.acs.AccessControl()
        return acs

    def create_weather(self):
        """
        Creates an instance of the Asset Service.
        """
        import predix.admin.weather
        weather = predix.admin.weather.WeatherForecast()
        weather.create()

        client_id = self.get_client_id()
        if client_id:
            weather.grant_client(client_id)

        weather.grant_client(client_id)
        weather.add_to_manifest(self.manifest_path)
        return weather

    def get_weather(self):
        """
        Returns an instance of the Weather Service.
        """
        import predix.data.weather
        weather = predix.data.weather.WeatherForecast()
        return weather
