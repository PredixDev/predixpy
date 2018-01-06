
import os
import logging
import tempfile
import unittest

import predix.admin.app
import predix.admin.cf.spaces

class TestPredixLogging(unittest.TestCase):
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
        cls.space.delete_space()
        print("Deleted test space %s" % (cls.space.name))

    def test_logstash_created(self):
        self.admin.create_logstash()

        created = False
        for service in self.admin.space.get_instances():
            if 'logstash' in service:
                created = True
                break
        self.assertTrue(created)


if __name__ == '__main__':
    if os.getenv('DEBUG'):
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()

