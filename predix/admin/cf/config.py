
import os
import json
import logging


class CloudFoundryLoginError(Exception):
    """
    A Cloud Foundry Login Error will be raised when the operation
    is not permitted due to an invalid token.
    """
    def __init__(self, message):
        super(CloudFoundryLoginError, self).__init__(message)
        logging.warning("Try 'cf login' to get a new token from Cloud Foundry (%s)." % (message))


class Config(object):
    """
    Interface into a cached cloud foundry configuration file.
    """
    def __init__(self, config_file='~/.cf/config.json', *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)

        logging.debug("Using CF config file: %s" % (config_file))
        self.config_file = config_file
        self.config = self._get_cloud_foundry_config()

    def _get_cloud_foundry_config(self):
        """
        Reads the local cf CLI cache stored in the users
        home directory.
        """
        config = os.path.expanduser(self.config_file)
        if not os.path.exists(config):
            raise CloudFoundryLoginError('You must run `cf login` to authenticate')

        with open(config, "r") as data:
            return json.load(data)

    def get_access_token(self):
        """
        Returns the access token from the cache, including the
        "Bearer" identifier.
        """
        return self.config['AccessToken']

    def get_uaa_endpoint(self):
        """
        Returns the UAA endpoint used for Predix Cloud Foundry
        authentication.
        """
        return self.config['UaaEndpoint']

    def get_target(self):
        """
        Returns the API target URI.
        """
        return self.config['Target']

    def _get_organization_info(self):
        """
        Returns all cached information about the org.
        """
        return self.config['OrganizationFields']

    def get_organization_name(self):
        """
        Returns the name of the organization currently targeted.
        """
        if 'PREDIX_ORGANIZATION_NAME' in os.environ:
            return os.environ['PREDIX_ORGANIZATION_NAME']
        else:
            return self._get_organization_info()['Name']

    def get_organization_guid(self):
        """
        Returns the GUID for the organization currently targeted.
        """
        if 'PREDIX_ORGANIZATION_GUID' in os.environ:
            return os.environ['PREDIX_ORGANIZATION_GUID']
        else:
            info = self._get_organization_info()
            for key in ('Guid', 'GUID'):
                if key in info.keys():
                    return info[key]
            raise ValueError('Unable to determine cf organization guid')

    def _get_space_info(self):
        """
        Returns all cached information about the space.
        """
        return self.config['SpaceFields']

    def get_space_name(self):
        """
        Returns the name of the space currently targeted.
        """
        if 'PREDIX_SPACE_NAME' in os.environ:
            return os.environ['PREDIX_SPACE_NAME']
        else:
            return self._get_space_info()['Name']

    def get_space_guid(self):
        """
        Returns the GUID for the space currently targeted.

        Can be set by environment variable with PREDIX_SPACE_GUID.
        Can be determined by ~/.cf/config.json.
        """
        if 'PREDIX_SPACE_GUID' in os.environ:
            return os.environ['PREDIX_SPACE_GUID']
        else:
            info = self._get_space_info()
            for key in ('Guid', 'GUID'):
                if key in info.keys():
                    return info[key]
            raise ValueError('Unable to determine cf space guid')
