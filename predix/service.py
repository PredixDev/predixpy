
import os
import json
import logging
import requests

import predix.security.uaa


class Service(object):
    """
    General class for making REST calls to Predix multi-tenant
    services that require a Predix-Zone-Id and Bearer token.
    """
    def __init__(self, zone, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)

        self.zone = zone

        self.uaa = predix.security.uaa.UserAccountAuthentication()
        self.session = requests.Session()

        self._auto_authenticate()

    def _auto_authenticate(self):
        """
        If we are in an app context we can authenticate immediately.
        """
        client_id = os.environ.get('PREDIX_APP_CLIENT_ID')
        client_secret = os.environ.get('PREDIX_APP_CLIENT_SECRET')

        if client_id and client_secret:
            logging.info("Automatically authenticated as %s" % (client_id))
            self.uaa.authenticate(client_id, client_secret)

    def _get_bearer_token(self):
        """
        For application client will return a valid bearer token.
        """
        return 'Bearer ' + self.uaa.get_token()

    def _get_headers(self):
        """
        Standard Predix service headers.
        """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Predix-Zone-Id': self.zone,
            'Authorization': self._get_bearer_token()
        }
        return headers

    def _get(self, uri, params=None):
        """
        Simple GET request for a given path.
        """
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

    def _post(self, uri, data):
        """
        Simple POST request for a given path.
        """
        headers = self._get_headers()

        logging.debug("URI=" + str(uri))
        logging.debug("BODY=" + json.dumps(data))

        response = self.session.post(uri, headers=headers,
                data=json.dumps(data))
        if response.status_code in [200, 204]:
            return response.json()
        else:
            logging.error(response.content)
            response.raise_for_status()

    def _put(self, uri, data):
        """
        Simple PUT operation for a given path.
        """
        headers = self._get_headers()

        logging.debug("URI=" + str(uri))
        logging.debug("BODY=" + json.dumps(data))

        response = self.session.put(uri, headers=headers,
                data=json.dumps(data))
        if response.status_code in [201, 204]:
            return data
        else:
            logging.error(response.content)
            response.raise_for_status()

    def _delete(self, uri):
        """
        Simple DELETE operation for a given path.
        """
        headers = self._get_headers()

        response = self.session.delete(uri, headers=headers)

        # Will return a 204 on successful delete
        if response.status_code == 204:
            return response
        else:
            logging.error(response.content)
            response.raise_for_status()

    def _patch(self, uri, data):
        """
        Simple PATCH operation for a given path.

        The body is expected to list operations to perform to update
        the data.  Operations include:
            - add
            - remove
            - replace
            - move
            - copy
            - test

        [
             { "op": "test", "path": "/a/b/c", "value": "foo" },
        ]
        """
        headers = self._get_headers()
        response = self.session.patch(uri, headers=headers,
                data=json.dumps(data))

        # Will return a 204 on successful patch
        if response.status_code == 204:
            return response
        else:
            logging.error(response.content)
            response.raise_for_status()
