
import os
import sys
import logging
import unittest

import six
if six.PY3:
    from unittest.mock import Mock, patch
else:
    from mock import Mock, patch

import predix.security.uaa


class TestUAA(unittest.TestCase):
    def setUp(self):
        self.uaa_uri = 'https://1234.predix-uaa.run.aws-usw02-pr.ice.predix.io'
        os.environ['PREDIX_SECURITY_UAA_URI'] = self.uaa_uri

    def test_init(self):
        uaa = predix.security.uaa.UserAccountAuthentication()
        self.assertIsInstance(uaa, predix.security.uaa.UserAccountAuthentication)

    def test_is_expired_token(self):
        uaa = predix.security.uaa.UserAccountAuthentication()
        self.assertTrue(uaa.is_expired_token(uaa.client))

    @patch('predix.security.uaa.requests.post')
    def test_authenticate(self, mock_post):

        # mock repsonse
        mock_post.return_value = Mock(ok=True, status_code=200)
        mock_post.return_value.json.return_value = {
            'access_token': 'eyJhb...5A1gw',
            'token_type': 'bearer',
            'jti': 'c07a740e...f1f6',
            'expires_in': 43199,
            'scope': 'uaa.resource uaa.none'
            }

        uaa = predix.security.uaa.UserAccountAuthentication()
        uaa.authenticate('masaya', 'masaya-yousaya', use_cache=False)

        uri = self.uaa_uri + '/oauth/token'
        expected_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic bWFzYXlhOm1hc2F5YS15b3VzYXlh',
                'Cache-Control': 'no-cache'
                }
        expected_params = {
                'grant_type': 'client_credentials',
                'client_id': 'masaya'
                }
        mock_post.assert_called_with(uri,
                headers=expected_headers,
                params=expected_params,
                )

        self.assertTrue(uaa.authenticated)
        self.assertFalse(uaa.is_expired_token(uaa.client))


if __name__ == '__main__':
    if os.getenv('DEBUG'):
        logging.basicConfig(level=logging.DEBUG)

    unittest.main()
