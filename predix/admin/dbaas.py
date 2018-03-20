
import os
import time
import logging

import predix.config
import predix.admin.service
import predix.data.dbaas

class PostgreSQL(object):
    """
    Predix Database as a Service provides a relational database management system
    (PostgreSQL) for data persistence.
    """
    def __init__(self, plan_name=None, name=None, uaa=None, *args, **kwargs):
        super(PostgreSQL, self).__init__(*args, **kwargs)
        self.service_name = 'postgres-2.0'
        self.plan_name = plan_name or 'dedicated-1.1'
        self.use_class = predix.data.dbaas.PostgreSQL

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

    def create(self, max_wait=300, allocated_storage=None,
            encryption_at_rest=None, restore_to_time=None, **kwargs):
        """
        Create an instance of the PostgreSQL service with the typical starting
        settings.

        :param max_wait: service is created asynchronously, so will only wait
            this number of seconds before giving up.

        :param allocated_storage: int for GBs to be allocated for storage

        :param encryption_at_rest: boolean for encrypting data that is stored

        :param restore_to_time: UTC date within recovery period for db
            backup to be used when initiating

        """

        # MAINT: Add these if there is demand for it and validated

        if allocated_storage or encryption_at_rest or restore_to_time:
            raise NotImplementedError()

        # Will need to wait for the service to be provisioned before can add
        # service keys and get env details.

        self.service.create(async=True, create_keys=False)
        while self._create_in_progress() and max_wait > 0:
            if max_wait % 5 == 0:
                logging.warning('Can take {}s for create to finish.'.format(max_wait))
            time.sleep(1)
            max_wait -= 1

        # Now get the service env (via service keys)
        cfg = self.service._get_service_config()
        self.service.settings.save(cfg)

        hostname = predix.config.get_env_key(self.use_class, 'hostname')
        os.environ[hostname] = self.service.settings.data['hostname']

        password = predix.config.get_env_key(self.use_class, 'password')
        os.environ[password] = self.service.settings.data['password']

        port = predix.config.get_env_key(self.use_class, 'port')
        os.environ[port] = str(self.service.settings.data['port'])

        username = predix.config.get_env_key(self.use_class, 'username')
        os.environ[username] = self.service.settings.data['username']

        uri = predix.config.get_env_key(self.use_class, 'uri')
        os.environ[uri] = self.service.settings.data['uri']

    def add_to_manifest(self, manifest):
        """
        Add useful details to the manifest about this service so
        that it can be used in an application.

        :param manifest: A predix.admin.app.Manifest object instance
            that manages reading/writing manifest config for a
            cloud foundry app.
        """
        manifest.add_service(self.service.name)

        hostname = predix.config.get_env_key(self.use_class, 'hostname')
        manifest.add_env_var(hostname, self.service.settings.data['hostname'])

        password = predix.config.get_env_key(self.use_class, 'password')
        manifest.add_env_var(password, self.service.settings.data['password'])

        port = predix.config.get_env_key(self.use_class, 'port')
        manifest.add_env_var(port, self.service.settings.data['port'])

        username = predix.config.get_env_key(self.use_class, 'username')
        manifest.add_env_var(username, self.service.settings.data['username'])

        uri = predix.config.get_env_key(self.use_class, 'uri')
        manifest.add_env_var(uri, self.service.settings.data['uri'])

        manifest.write_manifest()
