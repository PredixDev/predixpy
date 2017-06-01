
import os
import json
import errno
import base64
import logging
import requests
import datetime
import dateutil.parser

import predix.app

class UserAccountAuthentication(object):
    """
    The UAA service manages user account authorization and access control for
    Predix service calls through client credentials captured in a bearer token.

    Useful documentation about interacting with API here:
    https://docs.cloudfoundry.org/api/uaa
    """
    def __init__(self):

        self.uri = os.environ.get('PREDIX_UAA_URI')
        if not self.uri:
            raise ValueError("PREDIX_UAA_URI environment unset")

        self.authenticated = False
        self.client = None

    def _authenticate_client(self, client, secret):
        """
        Returns response of authenticating with the given client and
        secret.
        """
        credentials = base64.b64encode(str.join(':', [client, secret]))
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache',
            'Authorization': 'Basic ' + credentials
            }
        params = {
            'client_id': client,
            'grant_type': 'client_credentials'
            }
        uri = self.uri + '/oauth/token'

        logging.debug("URI=" + str(uri))
        logging.debug("HEADERS=" + str(headers))
        logging.debug("BODY=" + str(params))

        response = requests.post(uri, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def is_expired_token(self, client):
        """
        For a given client will test whether or not the token
        has expired.
        """
        if 'expires' not in client:
            return True

        expires = dateutil.parser.parse(client['expires'])
        if expires < datetime.datetime.now():
            return True

        return False

    def _initialize_uaa_cache(self):
        """
        If we don't yet have a uaa cache we need to 
        initialize it.  As there may be more than one
        UAA instance we index by issuer and then store
        any clients, users, etc.
        """
        try:
            os.makedirs(os.path.dirname(self._cache_path))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

        data = {}
        data[self.uri] = []

        return data

    def _read_uaa_cache(self):
        """
        Read cache of UAA client/user details.
        """
        self._cache_path = os.path.expanduser('~/.predix/uaa.json')
        if not os.path.exists(self._cache_path):
            return self._initialize_uaa_cache()

        with open(self._cache_path, 'r') as data:
            return json.load(data)

    def _get_client_from_cache(self, client_id):
        """
        For the given client_id return what is
        cached.
        """
        data = self._read_uaa_cache()

        # Only if we've cached any for this issuer
        if self.uri not in data:
            return

        for client in data[self.uri]:
            if client['id'] == client_id:
                return client

    def _write_to_uaa_cache(self, new_item):
        """
        Cache the client details into a cached file on disk.
        """
        data = self._read_uaa_cache()

        # Initialize client list if first time
        if self.uri not in data:
            data[self.uri] = []

        # Remove existing client record
        for client in data[self.uri]:
            if new_item['id'] == client['id']:
                data[self.uri].remove(client)

        data[self.uri].append(new_item)

        with open(self._cache_path, 'w') as output:
            output.write(json.dumps(data, sort_keys=True, indent=4))

    def authenticate(self, client_id, client_secret, use_cache=True):
        """
        Authenticate the given client against UAA.  The resulting token
        will be cached for reuse.
        """
        # We will reuse a token for as long as we have one cached
        # and it hasn't expired.
        if use_cache:
            client = self._get_client_from_cache(client_id)
            if (client) and (not self.is_expired_token(client)):
                self.authenticated = True
                self.client = client
                return

        # Let's authenticate the client
        client = {
            'id': client_id,
            'secret': client_secret
        }

        res = self._authenticate_client(client_id, client_secret)
        client.update(res)

        expires = datetime.datetime.now() + \
                  datetime.timedelta(seconds=res['expires_in'])
        client['expires'] = expires.isoformat()

        # Cache it for repeated use until expired
        self._write_to_uaa_cache(client)

        self.client = client
        self.authenticated = True

    def get_token(self):
        """
        Returns the bare access token for the authorized client.
        """
        if not self.authenticated:
            raise ValueError("Must authenticate client first.")

        # If token has expired we'll need to refresh and get a new
        # client credential
        if self.is_expired_token(self.client):
            logging.info("client token expired, will need to refresh token")
            self.authenticate(self.client['id'], self.client['secret'],
                    use_cache=False)

        return self.client['access_token']

    def get_scopes(self):
        """
        Returns the scopes for the authorized client.
        """
        if not self.authenticated:
            raise ValueError("Must authenticate client first.")

        scope = self.client['scope']
        return scope.split()

    def get_authorization_headers(self):
        """
        Returns the authorization headers with the bearer token needed for
        making calls to Predix Services protected by UAA.
        """
        return {
                'Authorization': 'Bearer ' + self.get_token()
                }

    def is_admin(self):
        """
        Test whether user is authenticated as the admin.
        """
        return self.authenticated and self.client['id'] == 'admin'

    def get_clients(self):
        """
        Returns the clients stored in the instance of UAA.
        """
        assert self.is_admin(), "Must be admin to get_clients()."

        uri = self.uri + '/oauth/clients'
        headers = self.get_authorization_headers()
        response = requests.get(uri, headers=headers)
        return response.json()['resources']

    def get_client(self, client_id):
        """
        Returns details about a specific client by the client_id.
        """
        uri = self.uri + '/oauth/clients/' + client_id
        headers = self.get_authorization_headers()
        response = requests.get(uri, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            # Not found but don't raise
            return

    def update_client_grants(self, client_id, scope=[], authorities=[],
            replace=False):
        """
        Will extend the client with any additional scopes or
        authorities.
        """
        client = self.get_client(client_id)
        if not client:
            raise ValueError("Must first create client: '%s'" % (client_id))

        if replace:
            changes = {
                'client_id': client_id,
                'scope': scope,
                'authorities': authorities,
                }
        else:
            changes = {'client_id': client_id}
            if scope:
                changes['scope'] = client['scope']
                changes['scope'].extend(scope)

            if authorities:
                changes['authorities'] = client['authorities']
                changes['authorities'].extend(authorities)

        uri = self.uri + '/oauth/clients/' + client_id
        headers = {
            "pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Accepts": "application/json",
            "Authorization": "Bearer " + self.get_token()
        }
        response = requests.put(uri, headers=headers, data=json.dumps(changes))

        if response.status_code == 200:
            return response
        else:
            response.raise_for_status()

    def create_client(self, client_id, client_secret, manifest=None):
        """
        Will create a new client for your application use.
        """
        assert self.is_admin(), "Must be admin to create_client()."

        # Check if client already exists
        client = self.get_client(client_id)
        if client:
            return client

        uri = self.uri + '/oauth/clients'
        headers = {
            "pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Accepts": "application/json",
            "Authorization": "Bearer " + self.get_token()
        }
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": ["uaa.none"],
            "authorized_grant_types": ["client_credentials", "refresh_token"],
            "authorities": ["uaa.none"],
            "autoapprove": []
        }

        response = requests.post(uri, headers=headers, data=json.dumps(params))
        if response.status_code == 201:
            if manifest:
                self.add_client_to_manifest(client_id, client_secret, manifest)

            client = {
                'id': client_id,
                'secret': client_secret
                }
            self._write_to_uaa_cache(client)
            return response
        else:
            response.raise_for_status()

    def add_client_to_manifest(self, client_id, client_secret, manifest_path):
        """
        Add the given client / secret to the manifest for use in
        the application.
        """
        manifest = predix.app.Manifest(manifest_path)
        manifest.add_env_var('PREDIX_APP_CLIENT_ID', client_id)
        manifest.add_env_var('PREDIX_APP_CLIENT_SECRET', client_secret)
        manifest.write_manifest()
