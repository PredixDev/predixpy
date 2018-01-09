
import os
import json
import errno
import base64
import logging
import requests
import datetime
import dateutil.parser

import predix.app
import predix.config

class UserAccountAuthentication(object):
    """
    The UAA service manages user account authorization and access control for
    Predix service calls through client credentials captured in a bearer token.

    :param uri: URI for the UAA endpoint to interact with, can be derived from
        environment PREDIX_SECURITY_UAA_URI variable when not specified.

    Useful documentation about interacting with API - https://docs.cloudfoundry.org/api/uaa

    And more documentation - https://github.com/cloudfoundry/uaa/tree/master/docs
    """
    def __init__(self, uri=None, *args, **kwargs):
        super(UserAccountAuthentication, self).__init__(*args, **kwargs)

        self.uri = uri or self._get_uaa_uri()
        self.session = requests.Session()
        self.authenticated = False
        self.client = {}

    def _get_uaa_uri(self):
        """
        Returns the URI endpoint for an instance of a UAA
        service instance from environment inspection.
        """
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            predix_uaa = services['predix-uaa'][0]['credentials']
            return predix_uaa['uri']
        else:
            return predix.config.get_env_value(self, 'uri')

    def _authenticate_client(self, client, secret):
        """
        Returns response of authenticating with the given client and
        secret.
        """
        client_s = str.join(':', [client, secret])
        credentials = base64.b64encode(client_s.encode('utf-8')).decode('utf-8')
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
            logging.debug("RESPONSE=" + str(response.json()))
            return response.json()
        else:
            logging.warning("Failed to authenticate as %s" % (client))
            response.raise_for_status()

    def _authenticate_user(self, user, password):
        """
        Returns the response of authenticating with the given
        user and password.
        """
        headers = self._get_headers()
        params = {
                'username': user,
                'password': password,
                'grant_type': 'password',
                }
        uri = self.uri + '/oauth/token'

        logging.debug("URI=" + str(uri))
        logging.debug("HEADERS=" + str(headers))
        logging.debug("BODY=" + str(params))

        response = requests.post(uri, headers=headers, params=params)
        if response.status_code == 200:
            logging.debug("RESPONSE=" + str(response.json()))
            return response.json()
        else:
            logging.warning("Failed to authenticate %s" % (user))
            response.raise_for_status()

    def is_expired_token(self, client):
        """
        For a given client will test whether or not the token
        has expired.

        This is for testing a client object and does not look up
        from client_id.  You can use _get_client_from_cache() to
        lookup a client from client_id.
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

        # Remove existing client record and any expired tokens
        for client in data[self.uri]:
            if new_item['id'] == client['id']:
                data[self.uri].remove(client)
                continue

            # May have old tokens laying around to be cleaned up
            if 'expires' in client:
                expires = dateutil.parser.parse(client['expires'])
                if expires < datetime.datetime.now():
                    data[self.uri].remove(client)
                    continue

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

    def logout(self):
        """
        Log currently authenticated user out, invalidating any existing tokens.
        """
        # Remove token from local cache
        # MAINT: need to expire token on server
        data = self._read_uaa_cache()
        if self.uri in data:
            for client in data[self.uri]:
                if client['id'] == self.client['id']:
                    data[self.uri].remove(client)

        with open(self._cache_path, 'w') as output:
            output.write(json.dumps(data, sort_keys=True, indent=4))

    def _get_headers(self):
        """
        Returns headers needed for UAA operations.
        """
        headers = {
            "pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Accepts": "application/json",
            "Authorization": "Bearer " + self.get_token()
        }
        return headers

    def _get(self, uri, params=None, headers=None):
        """
        Simple GET request for a given uri path.
        """
        if not headers:
            headers = self._get_headers()

        logging.debug("URI=" + str(uri))
        logging.debug("HEADERS=" + str(headers))

        response = self.session.get(uri, headers=headers, params=params)
        logging.debug("STATUS=" + str(response.status_code))
        if response.status_code == 200:
            return response.json()
        else:
            logging.error("ERROR=" + response.content)
            response.raise_for_status()

    def _post(self, uri, data, headers=None):
        """
        Simple POST request for a given uri path.
        """
        if not headers:
            headers = self._get_headers()

        logging.debug("URI=" + str(uri))
        logging.debug("HEADERS=" + str(headers))
        logging.debug("BODY=" + str(data))

        response = self.session.post(uri, headers=headers,
                data=json.dumps(data))

        logging.debug("STATUS=" + str(response.status_code))
        if response.status_code in [200, 201]:
            return response.json()
        else:
            logging.error("ERROR=" + response.content)
            response.raise_for_status()

    def get_token(self):
        """
        Returns the bare access token for the authorized client.
        """
        if not self.authenticated:
            raise ValueError("Must authenticate() as a client first.")

        # If token has expired we'll need to refresh and get a new
        # client credential
        if self.is_expired_token(self.client):
            logging.info("client token expired, will need to refresh token")
            self.authenticate(self.client['id'], self.client['secret'],
                    use_cache=False)

        return self.client['access_token']

    def get_scopes(self):
        """
        Returns the scopes for the authenticated client.
        """
        if not self.authenticated:
            raise ValueError("Must authenticate() as a client first.")

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

    def assert_has_permission(self, scope_required):
        """
        Warn that the required scope is not found in the scopes
        granted to the currently authenticated user.

        ::

            # The admin user should have client admin permissions
            uaa.assert_has_permission('admin', 'clients.admin')

        """
        if not self.authenticated:
            raise ValueError("Must first authenticate()")

        if scope_required not in self.get_scopes():
            logging.warning("Authenticated as %s" % (self.client['id']))
            logging.warning("Have scopes: %s" % (str.join(',', self.get_scopes())))
            logging.warning("Insufficient scope %s for operation" % (scope_required))

            raise ValueError("Client does not have permission.")

        return True

    def grant_client_permissions(self, client_id, admin=False, write=False,
            read=False, secret=False):
        """
        Grant the given client_id permissions for managing clients.

        - clients.admin: super user scope to create, modify, delete
        - clients.write: scope ot create and modify clients
        - clients.read: scope to read info about clients
        - clients.secret: scope to change password of a client

        """
        self.assert_has_permission('clients.admin')

        perms = []
        if admin:
            perms.append('clients.admin')

        if write or admin:
            perms.append('clients.write')

        if read or admin:
            perms.append('clients.read')

        if secret or admin:
            perms.append('clients.secret')

        if perms:
            self.update_client_grants(client_id, scope=perms,
                    authorities=perms)

    def get_clients(self):
        """
        Returns the clients stored in the instance of UAA.
        """
        self.assert_has_permission('clients.read')

        uri = self.uri + '/oauth/clients'
        headers = self.get_authorization_headers()
        response = requests.get(uri, headers=headers)
        return response.json()['resources']

    def get_client(self, client_id):
        """
        Returns details about a specific client by the client_id.
        """
        self.assert_has_permission('clients.read')

        uri = self.uri + '/oauth/clients/' + client_id
        headers = self.get_authorization_headers()
        response = requests.get(uri, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            # Not found but don't raise
            return

    def update_client_grants(self, client_id, scope=[], authorities=[],
            grant_types=[], redirect_uri=[], replace=False):
        """
        Will extend the client with additional scopes or
        authorities.  Any existing scopes and authorities will be left
        as is unless asked to replace entirely.
        """
        self.assert_has_permission('clients.write')

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

            if grant_types:
                if 'authorization_code' in grant_types and not redirect_uri:
                    logging.warning("A redirect_uri is required for authorization_code.")

                changes['authorized_grant_types'] = client['authorized_grant_types']
                changes['authorized_grant_types'].extend(grant_types)

            if redirect_uri:
                if 'redirect_uri' in client:
                    changes['redirect_uri'] = client['redirect_uri']
                    changes['redirect_uri'].extend(redirect_uri)
                else:
                    changes['redirect_uri'] = redirect_uri

        uri = self.uri + '/oauth/clients/' + client_id
        headers = {
            "pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Accepts": "application/json",
            "Authorization": "Bearer " + self.get_token()
        }

        logging.debug("URI=" + str(uri))
        logging.debug("HEADERS=" + str(headers))
        logging.debug("BODY=" + json.dumps(changes))

        response = requests.put(uri, headers=headers, data=json.dumps(changes))

        logging.debug("STATUS=" + str(response.status_code))
        if response.status_code == 200:
            return response
        else:
            logging.error(response.content)
            response.raise_for_status()

    def grant_scim_permissions(self, client_id, read=False, write=False,
            create=False, userids=False, zones=False, invite=False,
            openid=False):
        """
        Grant the given client_id permissions for managing users.  System
        for Cross-domain Identity Management (SCIM) are required for accessing
        /Users and /Groups endpoints of UAA.

        - scim.read: scope for read access to all SCIM endpoints
        - scim.write: scope for write access to all SCIM endpoints
        - scim.create: scope to create/invite users and verify an account only
        - scim.userids: scope for id and username+origin conversion
        - scim.zones: scope for group management of users only
        - scim.invite: scope to participate in invitations
        - openid: scope to access /userinfo

        """
        self.assert_has_permission('clients.admin')

        perms = []
        if read:
            perms.append('scim.read')

        if write:
            perms.append('scim.write')

        if create:
            perms.append('scim.create')

        if userids:
            perms.append('scim.userids')

        if zones:
            perms.append('scim.zones')

        if invite:
            perms.append('scim.invite')

        if openid:
            perms.append('openid')

        if perms:
            self.update_client_grants(client_id, scope=perms, authorities=perms)

    def create_client(self, client_id, client_secret, manifest=None,
            client_credentials=True, refresh_token=True,
            authorization_code=False, redirect_uri=[]):
        """
        Will create a new client for your application use.

        - client_credentials: allows client to get access token
        - refresh_token: can be used to get new access token when expired
          without re-authenticating
        - authorization_code: redirection-based flow for user authentication

        More details about Grant types:
        - https://github.com/cloudfoundry/uaa/blob/master/docs/UAA-Security.md
        - https://tools.ietf.org/html/rfc6749

        A redirect_uri is required when using authorization_code.  See:
        https://www.predix.io/support/article/KB0013026

        """
        self.assert_has_permission('clients.admin')

        if authorization_code and not redirect_uri:
            raise ValueError("Must provide a redirect_uri for clients used with authorization_code")

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

        grant_types = []

        if client_credentials:
            grant_types.append('client_credentials')
        if refresh_token:
            grant_types.append('refresh_token')
        if authorization_code:
            grant_types.append('authorization_code')

        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": ["uaa.none"],
            "authorized_grant_types": grant_types,
            "authorities": ["uaa.none"],
            "autoapprove": []
        }

        if redirect_uri:
            params.append(redirect_uri)

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
            logging.error(response.content)
            response.raise_for_status()

    def add_client_to_manifest(self, client_id, client_secret, manifest):
        """
        Add the given client / secret to the manifest for use in
        the application.
        """
        client_id_key = 'PREDIX_APP_CLIENT_ID'
        manifest.add_env_var(client_id_key, client_id)

        client_secret_key = 'PREDIX_APP_CLIENT_SECRET'
        manifest.add_env_var(client_secret_key, client_secret)

        manifest.write_manifest()

    def _post_user(self, data):
        """
        More complete control over creating users by calling the POST /Users
        directly.  The data should meet the UAA creation spec.

        More details:
        https://docs.cloudfoundry.org/api/uaa/#create-3
        """
        return self._post(self.uri + '/Users', data)

    def create_user(self, username, password, family_name, given_name, primary_email,
            details={}):
        """
        Creates a new user account with the required details.

        ::

            create_user('j12y', 'my-secret', 'Delancey', 'Jayson', 'volcano@ge.com')

        """
        self.assert_has_permission('scim.write')

        data = {
            'userName': username,
            'password': password,
            'name': {
                'familyName': family_name,
                'givenName': given_name,
                },
            'emails': [{
                'value': primary_email,
                'primary': True,
                }]
            }

        if details:
            data.update(details)

        return self._post_user(data)

    def delete_user(self, id):
        """
        Delete user with given id.
        """
        self.assert_has_permission('scim.write')

        uri = self.uri + '/Users/%s' % id
        headers = self._get_headers()

        logging.debug("URI=" + str(uri))
        logging.debug("HEADERS=" + str(headers))

        response = self.session.delete(uri, headers=headers)
        logging.debug("STATUS=" + str(response.status_code))
        if response.status_code == 200:
            return response
        else:
            logging.error(response.content)
            response.raise_for_status()

    def get_users(self, filter=None, sortBy=None, sortOrder=None,
            startIndex=None, count=None):
        """
        Returns users accounts stored in UAA.
        See https://docs.cloudfoundry.org/api/uaa/#list63

        For filtering help, see:
        http://www.simplecloud.info/specs/draft-scim-api-01.html#query-resources
        """
        self.assert_has_permission('scim.read')

        params = {}
        if filter:
            params['filter'] = filter

        if sortBy:
            params['sortBy'] = sortBy

        if sortOrder:
            params['sortOrder'] = sortOrder

        if startIndex:
            params['startIndex'] = startIndex

        if count:
            params['count'] = count

        return self._get(self.uri + '/Users', params=params)

    def get_user_by_username(self, username):
        """
        Returns details for user of the given username.

        If there is more than one match will only return the first.  Use
        get_users() for full result set.
        """
        results = self.get_users(filter='username eq "%s"' % (username))
        if results['totalResults'] == 0:
            logging.warning("Found no matches for given username.")
            return
        elif results['totalResults'] > 1:
            logging.warning("Found %s matches for username %s" %
                (results['totalResults'], username))

        return results['resources'][0]

    def get_user_by_email(self, email):
        """
        Returns details for user with the given email address.

        If there is more than one match will only return the first.  Use
        get_users() for full result set.
        """
        results = self.get_users(filter='email eq "%s"' % (email))
        if results['totalResults'] == 0:
            logging.warning("Found no matches for given email.")
            return
        elif results['totalResults'] > 1:
            logging.warning("Found %s matches for email %s" %
                (results['totalResults'], email))

        return results['resources'][0]

    def get_user(self, id):
        """
        Returns details about the user for the given id.

        Use get_user_by_email() or get_user_by_username() for help
        identifiying the id.
        """
        self.assert_has_permission('scim.read')
        return self._get(self.uri + '/Users/%s' % (id))

    def get_userinfo(self):
        """
        Retrieve user info for currently authenticated user.
        """
        return self._get(self.uri + '/userinfo')
