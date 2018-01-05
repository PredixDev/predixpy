
import os
import yaml
import copy
import logging
from cryptography.fernet import Fernet

import predix.config


class Manifest(object):
    """
    Cloud Foundry utilizes a MANIFEST.yml file as the source
    of application configuration.  As we setup services and
    run our applications the manifest is a place to store
    important configuration details.

    :param app_name: the name of your application which will be used by default
        in the route
    :param manifest_key: if encrypting your manifest this is the key for
        cryptography
    :param encrypted: whether to manifest values should be encrypted
    :param debug: enable additional debugging

    """
    def __init__(self, manifest_path='manifest.yml',
            app_name='my-predix-app',
            manifest_key='~/.predix/manifest_key',
            encrypted=False,
            debug=False):

        self.manifest_path = os.path.expanduser(manifest_path)
        self.app_name = app_name

        # Parameters for encrypting config files
        self.manifest_key = manifest_key
        self.encrypted = encrypted

        # App may have a client
        self.client_id = None
        self.client_secret = None

        if debug:
            logging.basicConfig(level=logging.DEBUG)

        # Read or Generate a manifest file
        if os.path.exists(self.manifest_path):
            self.read_manifest()
        else:
            self.create_manifest()

        # Probably always want manifest loaded into environment
        self.set_os_environ()

    def get_manifest_version(self):
        """
        Returns the version of PredixPy used to generate the manifest.
        """
        if 'env' in self.manifest:
            if 'PREDIXPY_VERSION' in self.manifest['env']:
                return self.manifest['env']['PREDIXPY_VERSION']

        return None

    def read_manifest(self, encrypted=None):
        """
        Read an existing manifest.
        """
        with open(self.manifest_path, 'r') as input_file:
            self.manifest = yaml.safe_load(input_file)
            if 'env' not in self.manifest:
                self.manifest['env'] = {}
            if 'services' not in self.manifest:
                self.manifest['services'] = []

            # If manifest is encrypted, use manifest key to
            # decrypt each value before storing in memory.

            if 'PREDIXPY_ENCRYPTED' in self.manifest['env']:
                self.encrypted = True

            if encrypted or self.encrypted:
                key = predix.config.get_crypt_key(self.manifest_key)
                f = Fernet(key)

                for var in self.manifest['env'].keys():
                    value = f.decrypt(self.manifest['env'][var])
                    self.manifest['env'][var] = value

            self.app_name = self.manifest['applications'][0]['name']

            input_file.close()

    def create_manifest(self):
        """
        Create a new manifest and write it to
        disk.
        """
        self.manifest = {}
        self.manifest['applications'] = [{'name': self.app_name}]
        self.manifest['services'] = []
        self.manifest['env'] = {
                'PREDIXPY_VERSION': str(predix.version),
                }

        self.write_manifest()

    def _get_encrypted_manifest(self):
        """
        Returns contents of the manifest where environment variables
        that are secret will be encrypted without modifying the existing
        state in memory which will remain unencrypted.
        """
        key = predix.config.get_crypt_key(self.manifest_key)
        f = Fernet(key)

        manifest = copy.deepcopy(self.manifest)
        for var in self.manifest['env'].keys():
            value = self.manifest['env'][var]
            manifest['env'][var] = f.encrypt(bytes(value))

        return manifest

    def write_manifest(self, manifest_path=None, encrypted=None):
        """
        Write manifest to disk.

        :param manifest_path: write to a different location
        :param encrypted: write with env data encrypted

        """
        manifest_path = manifest_path or self.manifest_path
        self.manifest['env']['PREDIXPY_VERSION'] = str(predix.version)

        with open(manifest_path, 'w') as output_file:
            if encrypted or self.encrypted:
                self.manifest['env']['PREDIXPY_ENCRYPTED'] = self.manifest_key
                content = self._get_encrypted_manifest()
            else:
                content = self.manifest   # shallow reference
                if 'PREDIXPY_ENCRYPTED' in content['env']:
                    del(content['env']['PREDIXPY_ENCRYPTED'])
                logging.warning("Writing manifest {} unencrypted.".format(manifest_path))

            yaml.safe_dump(content, output_file,
                    default_flow_style=False, explicit_start=True)
            output_file.close()

    def add_env_var(self, key, value):
        """
        Add the given key / value as another environment
        variable.
        """
        self.manifest['env'][key] = value
        os.environ[key] = str(value)

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
        self.client_id = predix.config.get_env_value(predix.app.Manifest, 'client_id')
        return self.client_id

    def get_client_secret(self):
        """
        Return the client secret that should correspond with
        the client id.
        """
        self.client_secret = predix.config.get_env_value(predix.app.Manifest, 'client_secret')
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

    def get_cache(self):
        import predix.data.cache
        cache = predix.data.cache.Cache()
        return cache
