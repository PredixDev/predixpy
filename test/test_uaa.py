
import unittest

import predix.security.uaa

class TestUAA(unittest.TestCase):
    def test_init(self):
        uaa = predix.security.uaa.UserAccountAuthentication()
        self.assertIsInstance(uaa, predix.security.uaa.UserAccountAuthentication)


if __name__ == '__main__':
    unittest.main()
