
import json
import logging
import requests

import predix.admin.cf.config


class API(object):
    """
    Manages Cloud Foundry API calls for system administration.

    Utilizes the local cf cli to cache identity and target details.  As
    a result developers must first `cf login`.

    More details:
    http://apidocs.cloudfoundry.org/
    """

    US_WEST = 'https://api.system.aws-usw02-pr.ice.predix.io'

    def __init__(self, *args, **kwargs):
        super(API, self).__init__(*args, **kwargs)

        self.config = predix.admin.cf.config.Config()
        self.session = requests.Session()

    def __del__(self):
        self.session.close()

    def _get_headers(self, content_type='application/json'):
        """
        Returns headers needed for talking to the Cloud Foundry
        Provider API endpoint.
        """
        headers = {
            'Accept': 'application/json',
            'Content-Type': content_type,
            'Authorization': self.config.get_access_token()
            }
        return headers

    def _post_headers(self):
        """
        Returns headers needed for talking to the Cloud Foundry
        Provider API endpoing for POST requests.
        """
        return self._get_headers(content_type='application/x-www-form-urlencoded')

    def get(self, path):
        """
        Generic GET with headers
        """
        uri = self.config.get_target() + path
        headers = self._get_headers()

        logging.debug("URI=GET " + str(uri))
        logging.debug("HEADERS=" + str(headers))

        response = self.session.get(uri, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise predix.admin.cf.config.CloudFoundryLoginError('token invalid')
        else:
            response.raise_for_status()

    def post(self, path, data):
        """
        Generic POST with headers
        """
        uri = self.config.get_target() + path
        headers = self._post_headers()

        logging.debug("URI=POST " + str(uri))
        logging.debug("HEADERS=" + str(headers))
        logging.debug("BODY=" + str(data))

        response = self.session.post(uri, headers=headers,
                data=json.dumps(data))
        if response.status_code in (200, 201, 202):
            return response.json()
        elif response.status_code == 401:
            raise predix.admin.cf.config.CloudFoundryLoginError('token invalid')
        else:
            logging.debug("STATUS=" + str(response.status_code))
            logging.debug("CONTENT=" + str(response.content))
            response.raise_for_status()

    def put(self, path, data):
        """
        Generic PUT with headers
        """
        uri = self.config.get_target() + path
        headers = self._get_headers()

        logging.debug("URI=PUT " + str(uri))
        logging.debug("HEADERS=" + str(headers))
        logging.debug("BODY=" + str(data))

        response = self.session.put(uri, headers=headers,
                data=json.dumps(data))

        if response.status_code in (200, 201, 202):
            return response
        elif response.status_code == 401:
            raise predix.admin.cf.config.CloudFoundryLoginError('token invalid')
        else:
            logging.debug("STATUS=" + str(response.status_code))
            logging.debug("CONTENT=" + str(response.content))
            response.raise_for_status()

    def delete(self, path, data=None, params=None):
        """
        Generic DELETE with headers
        """
        uri = self.config.get_target() + path
        headers = {
            'Authorization': self.config.get_access_token()
            }

        logging.debug("URI=DELETE " + str(uri))
        logging.debug("HEADERS=" + str(headers))

        response = self.session.delete(
            uri, headers=headers, params=params, data=json.dumps(data))

        if response.status_code == 204:
            return response
        else:
            logging.debug("STATUS=" + str(response.status_code))
            logging.debug("CONTENT=" + str(response.content))
            response.raise_for_status()

    def get_info(self):
        """
        Return API info such as:

            - api_version
            - authorization_endpoint
            - doppler_logging_endpoint
            - logging_endpoint
            - min_cli_version
        """
        return self.get('/v2/info')
