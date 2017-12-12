
import os
import logging
import tempfile
import unittest

import predix
import predix.admin.app

class TestManifest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.manifest_path = tempfile.mktemp(suffix='.yml', prefix='manifest_')
        logging.debug(cls.manifest_path)
        cls.admin = predix.admin.app.Manifest(cls.manifest_path)

        with open(cls.manifest_path, 'r') as m:
            cls.manifest_content = m.read()
            m.close()

    def _get_test_data_file(self, filename):
        return os.path.join(os.path.dirname(__file__), 'data', filename)

    def test_version_written(self):
        # Verify environment variable set for version tracking
        self.assertEqual(os.getenv('PREDIXPY_VERSION'), predix.version)

        # Verify creating a new manifest will write version
        self.assertTrue('PREDIXPY_VERSION' in self.manifest_content)

    def test_version_read_backward_compatible(self):
        # Verify reading exising manifest without a version handled
        manifest_path = self._get_test_data_file('manifest_empty_noversion.yml')
        admin = predix.admin.app.Manifest(manifest_path)

        self.assertEqual(admin.app_name, 'manifest-empty-noversion')
        self.assertEqual(admin.get_manifest_version(), None)

    def test_version_read(self):
        # Verify reading existing manifest with a version handled
        manifest_path = self._get_test_data_file('manifest_empty_version.yml')
        admin = predix.admin.app.Manifest(manifest_path)

        self.assertEqual(admin.app_name, 'my-predix-app')
        self.assertEqual(admin.get_manifest_version(), '0.0.9')


if __name__ == '__main__':
    if os.getenv('DEBUG'):
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()
