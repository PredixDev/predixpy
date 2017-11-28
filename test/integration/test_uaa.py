
import os
import sys
import logging
import unittest
import tempfile

import predix.admin.app
import predix.admin.cf.spaces

class TestUAA(unittest.TestCase):

    def setUp(self):
        self.space = predix.admin.cf.spaces.create_temp_space()
        self.manifest_path = tempfile.mktemp(suffix='.yml', prefix='manifest_')
        print("Created space %s" % (self.space.name))

        self.admin = predix.admin.app.Manifest(self.manifest_path)
        self.admin.create_uaa(self.space.name)
        self.admin.create_client('client-id', self.space.name)

        self.app = predix.app.Manifest(self.manifest_path)

    def tearDown(self):
        self.space.delete_space()
        print("Deleted space %s" % (self.space.name))

    def test_client(self):
        uaa = self.app.get_uaa()

        self.assertEqual(self.app.get_client_id(), 'client-id')
        self.assertEqual(self.app.get_client_secret(), self.space.name)

        uaa.authenticate(self.app.get_client_id(),
                self.app.get_client_secret())

        self.assertFalse(uaa.is_admin())
        self.assertEqual(uaa.get_scopes(), [u'uaa.none'])
        self.assertTrue(len(uaa.get_token()) > 900)



if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    unittest.main()
