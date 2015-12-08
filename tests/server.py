# See file COPYING distributed with xnatrest for copyright and license.

import unittest
from . import config
import xnatrest

class TestServer(unittest.TestCase):

    def test_redirect(self):
        server = xnatrest.Server('http://central.xnat.org')
        self.assertEqual(server.parsed.scheme, 'https')
        self.assertEqual(server.parsed.netloc, 'central.xnat.org')
        self.assertEqual(server.parsed.path, '/')
        return

    @config.test_foreach('non-xnat')
    def test_non_xnat(self, server_info):
        with self.assertRaises(xnatrest.UnidentifiedServerError):
            xnatrest.Server(server_info['url'])
        return

    @config.test_foreach('version')
    def test_version(self, server_info):
        s = xnatrest.Server(server_info['url'])
        self.assertEqual(s.version, server_info['version'], server_info['name'])
        return

"""
    def test_nojsessionid(self):
        with self.assertRaises(xnatrest.JSESSIONIDError):
            c = xnatrest.Connection(config.non_xnat_url)
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
"""

# eof
