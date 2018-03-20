
import os
import logging
import tempfile
import unittest

import predix.admin.app
import predix.admin.cf.spaces

class TestPredixCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.space = predix.admin.cf.spaces.create_temp_space()
        cls.manifest_path = tempfile.mktemp(suffix='.yml', prefix='manifest_')
        print("Created test space {}".format(cls.space.name))
        print("Created manifest {}".format(cls.manifest_path))

        cls.admin = predix.admin.app.Manifest(cls.manifest_path,
                encrypted=True)

    @classmethod
    def tearDownClass(cls):
        # TODO: pending work to delete the space async
        # cls.space.delete_space()
        print("Deleted test space %s" % (cls.space.name))

    def test_create_cache(self):
        self.admin.create_cache()

        name = self.space.name + '-predix-cache-shared-r30'
        self.assertTrue(name in self.admin.space.get_instances())


if __name__ == '__main__':
    if os.getenv('DEBUG'):
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()
