
import os
import yaml
import logging


class Manifest(object):
    """
    Cloud Foundry utilizes a MANIFEST.yml file as the source
    of application configuration.  As we setup services and
    run our applications the manifest is a place to store
    important configuration details.
    """
    def __init__(self, manifest_path='manifest.yml', app_name='my-predix-app', debug=False):
        self.manifest_path = os.path.expanduser(manifest_path)
        self.app_name = app_name

        # App may have a client
        self.client_id = None
        self.client_secret = None

        if debug:
            logging.basicConfig(level=logging.DEBUG)

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
        os.environ[key] = value

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
        key = 'PREDIX_APP_CLIENT_ID'
        if key not in self.manifest['env']:
            raise ValueError("%s undefined in manifest." % key)

        self.client_id = self.manifest['env'][key]
        return self.client_id

    def get_client_secret(self):
        """
        Return the client secret that should correspond with
        the client id.
        """
        key = 'PREDIX_APP_CLIENT_SECRET'
        if key not in self.manifest['env']:
            raise ValueError("%s must be added to manifest." % key)

        self.client_secret = self.manifest['env'][key]
        return self.client_secret

    def get_timeseries(self, *args, **kwargs):
        """
        Returns an instance of the Time Series Service.
        """
        import predix.data.timeseries
        ts = predix.data.timeseries.TimeSeries(*args, **kwargs)
        return ts

    def get_asset(self):
        """
        Returns an instance of the Asset Service.
        """
        import predix.data.asset
        asset = predix.data.asset.Asset()
        return asset

    def get_uaa(self):
        """
        Returns an insstance of the UAA Service.
        """
        import predix.security.uaa
        uaa = predix.security.uaa.UserAccountAuthentication()
        return uaa

    def get_acs(self):
        """
        Returns an instance of the Asset Control Service.
        """
        import predix.security.acs
        acs = predix.security.acs.AccessControl()
        return acs

    def get_weather(self):
        """
        Returns an instance of the Weather Service.
        """
        import predix.data.weather
        weather = predix.data.weather.WeatherForecast()
        return weather

    def get_blobstore(self):
        import predix.data.blobstore
        blobstore = predix.data.blobstore.BlobStore()
        return blobstore
