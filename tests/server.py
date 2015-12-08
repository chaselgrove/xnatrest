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

# eof
