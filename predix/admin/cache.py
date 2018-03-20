
import os
import time

import predix.config
import predix.admin.service
import predix.data.cache

class Cache(object):
    """
    Predix Cache key-value persistent storage.
    """
    def __init__(self, plan_name=None, name=None, uaa=None, *args, **kwargs):
        super(Cache, self).__init__(*args, **kwargs)
        self.service_name = 'predix-cache'
        self.plan_name = plan_name or 'Shared-R30'
        self.use_class = predix.data.cache.Cache

        self.service = predix.admin.service.CloudFoundryService(self.service_name,
                self.plan_name, name=name)

    def exists(self):
        """
        Returns whether or not this service already exists.
        """
        return self.service.exists()

    def _create_in_progress(self):
        """
        Creating this service is handled asynchronously so this method will
        simply check if the create is in progress.  If it is not in progress,
        we could probably infer it either failed or succeeded.
        """
        instance = self.service.service.get_instance(self.service.name)
        if (instance['last_operation']['state'] == 'in progress' and
           instance['last_operation']['type'] == 'create'):
               return True

        return False

    def create(self, max_wait=180, **kwargs):
        """
        Create an instance of the Predix Cache Service with they typical
        starting settings.

        :param max_wait: service is created asynchronously, so will only wait
            this number of seconds before giving up.

        """
        # Will need to wait for the service to be provisioned before can add
        # service keys and get env details.
        self.service.create(async=True, create_keys=False)
        while self._create_in_progress() and max_wait > 0:
            time.sleep(1)
            max_wait -= 1

        # Now get the service env (via service keys)
        cfg = self.service._get_service_config()
        self.service.settings.save(cfg)

        host = predix.config.get_env_key(self.use_class, 'host')
        os.environ[host] = self.service.settings.data['host']

        password = predix.config.get_env_key(self.use_class, 'password')
        os.environ[password] = self.service.settings.data['password']

        port = predix.config.get_env_key(self.use_class, 'port')
        os.environ[port] = str(self.service.settings.data['port'])

    def add_to_manifest(self, manifest):
        """
        Add useful details to the manifest about this service so
        that it can be used in an application.

        :param manifest: A predix.admin.app.Manifest object instance
            that manages reading/writing manifest config for a
            cloud foundry app.
        """
        manifest.add_service(self.service.name)

        host = predix.config.get_env_key(self.use_class, 'host')
        manifest.add_env_var(host, self.service.settings.data['host'])

        password = predix.config.get_env_key(self.use_class, 'password')
        manifest.add_env_var(password, self.service.settings.data['password'])

        port = predix.config.get_env_key(self.use_class, 'port')
        manifest.add_env_var(port, self.service.settings.data['port'])

        manifest.write_manifest()
