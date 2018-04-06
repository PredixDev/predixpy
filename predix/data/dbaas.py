
import os
import json
import logging
import sqlalchemy

import predix.service
import predix.config

class PostgreSQL(object):
    """
    A Relational Database Management System on demand (PostgreSQL).

    .. important::

       This service will only work from the Predix Cloud -- Firewall will block
       any traffic not originating from within the Predix environment.  If you
       attempt you'll likely see a ConnectionError *Error 60* with *Operation
       timed out.*

    For more information about Predix Database as a Service see the catalog and
    official documentation.

    https://www.predix.io/services/service.html?id=1178
    """
    def __init__(self, hostname=None, port=None, username=None, password=None,
            database=None, *args, **kwargs):

        if not predix.config.is_cf_env():
            raise predix.config.PredixCloudRequiredError()

        self.hostname = hostname or self._get_hostname()
        self.port = port or self._get_port()
        self.username = username or self._get_username()
        self.password = password or self._get_password()
        self.database = database or 'postgres'

        connection_str = 'postgresql://{}:{}@{}:{}/{}'.format(
                self.username,
                self.password,
                self.hostname,
                self.port,
                self.database,
                )
        self.engine = sqlalchemy.create_engine(connection_str)

    def __del__(self):
        if self.engine:
            # self.engine.close()
            pass

    def _get_hostname(self):
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            postgres = services['postgres-2.0'][0]['credentials']
            return postgres['hostname']
        else:
            return predix.config.get_env_value(self, 'hostname')

    def _get_port(self):
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            postgres = services['postgres-2.0'][0]['credentials']
            return postgres['port']
        else:
            return predix.config.get_env_value(self, 'port')

    def _get_username(self):
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            postgres = services['postgres-2.0'][0]['credentials']
            return postgres['username']
        else:
            return predix.config.get_env_value(self, 'username')

    def _get_password(self):
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            postgres = services['postgres-2.0'][0]['credentials']
            return postgres['password']
        else:
            return predix.config.get_env_value(self, 'password')

    def execute(self, statement, *args, **kwargs):
        """
        This convenience method will execute the query passed in as is.  For
        more complex functionality you may want to use the sqlalchemy engine
        directly, but this serves as an example implementation.

        :param select_query: SQL statement to execute that will identify the
            resultset of interest.

        """
        with self.engine.connect() as conn:
            s = sqlalchemy.sql.text(statement)
            return conn.execute(s, **kwargs)
