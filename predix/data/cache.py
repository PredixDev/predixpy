import os
import json
import redis
import logging

import predix.service
import predix.config

class Cache(object):
    """
    A simple Key-Value in memory data store (Redis).

    .. important::

       This service will only work from the Predix Cloud -- Firewall will block
       any traffic not originating from within the Predix environment.  If you
       attempt you'll likely see a ConnectionError *Error 60* with *Operation
       timed out.*

    For more information about Predix Cache see the catalog and official
    documentation.

    https://www.predix.io/services/service.html?id=1215

    """
    def __init__(self, host=None, port=None, password=None,
            *args, **kwargs):

        if not predix.config.is_cf_env():
            raise ValueError("This service can only be used in the Predix Cloud Foundry environment.")

        self.host = host or self._get_host()
        self.port = port or self._get_port()
        self.password = password or self._get_password()

        self.connection = redis.StrictRedis(host=self.host, port=self.port,
                password=self.password)

    def _get_host(self):
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            predix_cache = services['predix-cache'][0]['credentials']
            return predix_cache['host']
        else:
            return predix.config.get_env_value(self, 'host')

    def _get_password(self):
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            predix_cache = services['predix-cache'][0]['credentials']
            return predix_cache['password']
        else:
            return predix.config.get_env_value(self, 'password')

    def _get_port(self):
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            predix_cache = services['predix-cache'][0]['credentials']
            return predix_cache['port']
        else:
            return predix.config.get_env_value(self, 'port')

    def get(self, key):
        """
        Return the value stored for the given key.
        """
        return self.connection.get(key)

    def set(self, key, value):
        """
        Set the given key to the given value.
        """
        return self.connection.set(key, value)
