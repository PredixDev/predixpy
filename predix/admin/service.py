
import logging

import predix.admin.uaa
import predix.admin.config
import predix.admin.cf.services


class CloudFoundryService(object):
    """
    Cloud Foundry Services
    """
    def __init__(self, service_name, plan_name, name=None, *args, **kwargs):
        super(CloudFoundryService, self).__init__(*args, **kwargs)
        self.service = predix.admin.cf.services.Service()

        # Basic details needed for creating the service
        self.plan_name = plan_name
        self.service_name = service_name
        self.name = name or self._generate_name(self.service.space.name, service_name, plan_name)

        # Cache for service configuration details
        self.config_path = self._get_config_path()
        self.settings = predix.admin.config.ServiceConfig(self.config_path)

    def _generate_name(self, space, service_name, plan_name):
        """
        Can generate a name based on the space, service name and plan.
        """
        return str.join('-', [space, service_name, plan_name]).lower()

    def _get_config_path(self):
        """
        Return a sensible configuration path for caching config
        settings.
        """
        org = self.service.space.org.name
        space = self.service.space.name
        name = self.name

        return "~/.predix/%s/%s/%s.json" % (org, space, name)

    def _create_service(self, parameters={}):
        """
        Create a Cloud Foundry service that has custom parameters.
        """
        logging.debug("_create_service()")
        logging.debug(str.join(',', [self.service_name, self.plan_name,
            self.name, str(parameters)]))
        return self.service.create_service(self.service_name, self.plan_name,
                self.name, parameters)

    def _delete_service(self, service_only=False):
        """
        Delete a Cloud Foundry service and any associations.
        """
        logging.debug('_delete_service()')
        # delete this ser
        pass

    def _get_or_create_service_key(self):
        """
        Get a service key or create one if needed.
        """
        keys = self.service._get_service_keys(self.name)
        for key in keys['resources']:
            if key['entity']['name'] == self.service_name:
                return self.service.get_service_key(self.name,
                        self.service_name)

        self.service.create_service_key(self.name, self.service_name)
        return self.service.get_service_key(self.name, self.service_name)

    def _get_service_config(self):
        """
        Will get configuration for the service from a service key.
        """
        key = self._get_or_create_service_key()

        config = {}
        config['service_key'] = [{'name': self.name}]
        config.update(key['entity']['credentials'])

        return config

    def exists(self):
        """
        Test whether or not this service already exists.
        """
        return self.service.space.has_service_with_name(self.name)

    def create(self, parameters={}):
        """
        Create the service.
        """
        # Create the service
        cs = self._create_service(parameters=parameters)

        # Create the service key to get config details and
        # store in local cache file.
        cfg = parameters
        cfg.update(self._get_service_config())
        self.settings.save(cfg)


class PredixService(CloudFoundryService):
    """
    Predix Services extend Cloud Foundry Services by providing
    UAA protections in some standard ways.
    """
    def __init__(self, service_name, plan_name, uaa=None, *args, **kwargs):
        super(PredixService, self).__init__(service_name, plan_name, *args, **kwargs)

        # We will create a UAA instance if not given one and authenticate
        self.uaa = self._get_or_create_uaa(uaa)

    def _get_or_create_uaa(self, uaa):
        """
        Returns a valid UAA instance for performing administrative functions
        on services.
        """
        if isinstance(uaa, predix.admin.uaa.UserAccountAuthentication):
            return uaa

        logging.debug("Initializing a new UAA")
        return predix.admin.uaa.UserAccountAuthentication()

    def create(self, parameters={}):
        """
        Create an instance of the US Weather Forecast Service with
        typical starting settings.
        """
        # Add parameter during create for UAA issuer
        uri = self.uaa.service.settings.data['uri'] + '/oauth/token'
        parameters["trustedIssuerIds"] = [uri]
        super(PredixService, self).create(parameters=parameters)
