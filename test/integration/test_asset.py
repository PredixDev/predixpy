
import os
import time
import logging
import tempfile
import unittest

import predix.admin.app
import predix.admin.cf.spaces

class TestAsset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.space = predix.admin.cf.spaces.create_temp_space()
        cls.manifest_path = tempfile.mktemp(suffix='.yml', prefix='manifest_')
        print("Created test space {}".format(cls.space.name))
        print("Created manifest {}".format(cls.manifest_path))

        cls.admin = predix.admin.app.Manifest(cls.manifest_path,
                encrypted=False)
        cls.admin.create_uaa(cls.space.name)
        cls.admin.create_client('client-id', cls.space.name)
        cls.admin.create_asset()

        cls.app = predix.app.Manifest(cls.manifest_path)

    @classmethod
    def tearDownClass(cls):
        cls.space.delete_space()
        print("Deleted test space %s" % (cls.space.name))

    def test_post_asset(self):
        asset = self.app.get_asset()

        # Issue #19: post_collection() raised ValueError with empty response
        volcano = {
                'uri': '/volcano/masaya',
                'name': 'Masaya',
                'location': {
                    'lat': 11.98531829999,
                    'long': -86.1783429000,
                    },
                'description': 'Masaya, Nicaragua',
                }

        asset.post_collection('/volcano', [volcano])
        self.assertTrue('volcano' in asset.get_collections())

    def test_asset_created(self):
        asset = self.app.get_asset()
        self.assertIsInstance(asset, predix.data.asset.Asset)

if __name__ == '__main__':
    if os.getenv('DEBUG'):
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()
