
import os
import sys
import logging
import unittest
import tempfile

import predix.admin.app
import predix.admin.cf.spaces

class TestUAA(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.space = predix.admin.cf.spaces.create_temp_space()
        cls.manifest_path = tempfile.mktemp(suffix='.yml', prefix='manifest_')
        print("Created test space %s" % (cls.space.name))

        cls.admin = predix.admin.app.Manifest(cls.manifest_path)
        cls.admin.create_uaa(cls.space.name)
        cls.admin.create_client('client-id', cls.space.name)

        cls.app = predix.app.Manifest(cls.manifest_path)

    @classmethod
    def tearDownClass(cls):
        cls.space.delete_space()
        print("Deleted test space %s" % (cls.space.name))

    def test_client(self):
        uaa = self.app.get_uaa()

        self.assertEqual(self.app.get_client_id(), 'client-id')
        self.assertEqual(self.app.get_client_secret(), self.space.name)

        uaa.authenticate(self.app.get_client_id(),
                self.app.get_client_secret())

        self.assertFalse(uaa.is_admin())
        self.assertEqual(uaa.get_scopes(), [u'uaa.none'])
        self.assertTrue(len(uaa.get_token()) > 900)

    def test_client_management(self):
        uaa = self.app.get_uaa()

        # Authenticate as the admin user to create a superuser
        uaa.authenticate('admin', self.space.name)
        uaa.create_client('superman-id', 'superman-secret')
        uaa.grant_client_permissions('superman-id', admin=True)

        # Authenticate as the superuser and verify permissions
        uaa.authenticate('superman-id', 'superman-secret')
        self.assertTrue(uaa.assert_has_permission('clients.admin'))
        self.assertEqual(len(uaa.get_scopes()), 5)

    def test_user_management(self):
        uaa = self.app.get_uaa()

        # Authenticate as the admin user to create a user manager
        uaa.authenticate('admin', self.space.name)
        uaa.create_client('userman-id', 'userman-secret')
        uaa.grant_scim_permissions('userman-id', read=True, write=True,
                openid=True)

        # Authenticate as the user manager and verify CRD operations
        uaa.authenticate('userman-id', 'userman-secret')
        uaa.create_user('j12y', 'password123', 'DeLancey', 'Jayson', 'jayson.delancey@ge.com')
        uaa.create_user('masaya', 'volcano123', 'Hell', 'Mouth', 'volcano@ge.com')

        users = uaa.get_users()
        self.assertEqual(users['totalResults'], 2)

        user = uaa.get_user_by_username('j12y')
        self.assertEqual(user['emails'][0]['value'], 'jayson.delancey@ge.com')

        uaa.delete_user(user['id'])
        users = uaa.get_users()
        self.assertEqual(users['totalResults'], 1)

        # Should not have permission to create clients
        with self.assertRaises(ValueError):
            uaa.create_client('aviation', 'aviator123')

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    unittest.main()
