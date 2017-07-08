
import os

import predix.config
import predix.admin.service
import predix.data.blobstore


class BlobStore(object):
    """
    Blob Store for binary large object storage.
    """
    def __init__(self, plan_name=None, name=None, uaa=None, *args, **kwargs):
        super(BlobStore, self).__init__(*args, **kwargs)
        self.service_name = 'predix-blobstore'
        self.plan_name = plan_name or 'Tiered'
        self.use_class = predix.data.blobstore.BlobStore

        self.service = predix.admin.service.CloudFoundryService(self.service_name,
                self.plan_name, name=name)

    def exists(self):
        """
        Returns whether or not this service already exists.
        """
        return self.service.exists()

    def create(self):
        """
        Create an instance of the Blob Store Service with the typical
        starting settings.
        """
        self.service.create()

        url = predix.config.get_env_key(self.use_class, 'url')
        os.environ[url] = self.service.settings.data['url']

        access_key_id = predix.config.get_env_key(self.use_class, 'access_key_id')
        os.environ[access_key_id] = self.service.settings.data['access_key_id']

        bucket_name = predix.config.get_env_key(self.use_class, 'bucket_name')
        os.environ[bucket_name] = self.service.settings.data['bucket_name']

        host = predix.config.get_env_key(self.use_class, 'host')
        os.environ[host] = self.service.settings.data['host']

        secret_access_key = predix.config.get_env_key(self.use_class,
                'secret_access_key')
        os.environ[secret_access_key] = self.service.settings.data['secret_access_key']


    def add_to_manifest(self, manifest):
        """
        Add useful details to the manifest about this service
        so that it can be used in an application.

        :param manifest: An predix.admin.app.Manifest object
            instance that manages reading/writing manifest config
            for a cloud foundry app.
        """
        # Add this service to the list of services
        manifest.add_service(self.service.name)

        # Add environment variables

        url = predix.config.get_env_key(self.use_class, 'url')
        manifest.add_env_var(url, self.service.settings.data['url'])

        akid = predix.config.get_env_key(self.use_class, 'access_key_id')
        manifest.add_env_var(akid, self.service.settings.data['access_key_id'])

        bucket = predix.config.get_env_key(self.use_class, 'bucket_name')
        manifest.add_env_var(bucket, self.service.settings.data['bucket_name'])

        host = predix.config.get_env_key(self.use_class, 'host')
        manifest.add_env_var(host, self.service.settings.data['host'])

        secret_access_key = predix.config.get_env_key(self.use_class, 'secret_access_key')
        manifest.add_env_var(secret_access_key, self.service.settings.data['secret_access_key'])

        manifest.write_manifest()

    def enable_encryption(self):
        os.environ['ENABLE_SERVER_SIDE_ENCRYPTION'] = True
