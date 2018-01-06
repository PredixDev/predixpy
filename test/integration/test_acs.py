
import os
import time
import logging
import tempfile
import unittest

import predix.admin.app
import predix.admin.cf.spaces

class TestAccessControl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.space = predix.admin.cf.spaces.create_temp_space()
        cls.manifest_path = tempfile.mktemp(suffix='.yml', prefix='manifest_')
        print("Created test space {}".format(cls.space.name))
        print("Created manifest {}".format(cls.manifest_path))

        cls.admin = predix.admin.app.Manifest(cls.manifest_path,
                encrypted=True)
        cls.admin.create_uaa(cls.space.name)
        cls.admin.create_client('client-id', cls.space.name)
        cls.admin.create_acs()

        cls.app = predix.app.Manifest(cls.manifest_path)

    @classmethod
    def tearDownClass(cls):
        cls.space.delete_space()
        print("Deleted test space %s" % (cls.space.name))

    def test_timeseries_created(self):
        acs = self.app.get_acs()
        self.assertIsInstance(acs, predix.security.acs.AccessControl)

if __name__ == '__main__':
    if os.getenv('DEBUG'):
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()

