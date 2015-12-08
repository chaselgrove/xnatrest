# See file COPYING distributed with xnatrest for copyright and license.

import unittest
from . import config
import xnatrest

class TestJsession(unittest.TestCase):

    @config.test_foreach('jsession')
    def test_get_noauth(self, server_info):
        server = xnatrest.Server(server_info['url'])
        resource = xnatrest.JsessionResource(server)
        response = resource.get()
        self.assertEqual(response.status, 200, server_info['name'])
        return

    @config.test_foreach('jsession')
    def test_get_token_auth(self, server_info):
        server = xnatrest.Server(server_info['url'])
        resource = xnatrest.JsessionResource(server)
        response = resource.get()
        token = response.data
        headers = {'Cookie': 'JSESSIONID=%s' % token}
        response2 = resource.get(headers=headers)
        self.assertEqual(response2.status, 200, server_info['name'])
        self.assertEqual(response2.data, token, server_info['name'])
        return

    @config.test_foreach('jsession')
    def test_put(self, server_info):
        server = xnatrest.Server(server_info['url'])
        resource = xnatrest.JsessionResource(server)
        response = resource.put()
        self.assertEqual(response.status, 405, server_info['name'])
        return

#    @config.test_foreach('jsession')
#    def test_post_delete(self, server_info):
#        server = xnatrest.Server(server_info['url'])
#        resource = xnatrest.JsessionResource(server)

# eof
