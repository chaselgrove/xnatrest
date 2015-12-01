# See file COPYING distributed with xnatrest for copyright and license.

import unittest
import xnatrest

class TestConnection(unittest.TestCase):

    def test_redirect(self):
        c = xnatrest.Connection('http://central.xnat.org')
        self.assertEqual(c.server.scheme, 'https')
        self.assertEqual(c.server.netloc, 'central.xnat.org')
        self.assertEqual(c.server.path, '/')
        return

    def test_nojsessionid(self):
        with self.assertRaises(xnatrest.JSESSIONIDError):
            c = xnatrest.Connection('http://www.nitrc.org')
        return

    def test_version(self):
        c = xnatrest.Connection('http://www.nitrc.org/ir')
        self.assertEqual(c.version, '1.5.4')
        return

    def test_bad_auth(self):
        with self.assertRaises(xnatrest.AuthenticationError):
            c = xnatrest.Connection('https://central.xnat.org/')
            c.auth_user_password('nosetests', 'bogus')
        return

    def test_auth(self):
        c = xnatrest.Connection('https://central.xnat.org/')
        self.assertEqual(c.auth_type, 'jsessionid')
        self.assertIsNone(c.user)
        c.auth_jsessionid('nosetests', 'nose')
        self.assertEqual(c.auth_type, 'jsessionid')
        self.assertEqual(c.user, 'nosetests')
        c.auth_anonymous()
        self.assertEqual(c.auth_type, 'jsessionid')
        self.assertIsNone(c.user)
        jsessionid = c._jsessionid
        c.auth_anonymous()
        self.assertNotEqual(c._jsessionid, jsessionid)
        return

# eof
