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
        response2 = resource.get(auth=token)
        self.assertEqual(response2.status, 200, server_info['name'])
        self.assertEqual(response2.data, token, server_info['name'])
        return

    @config.test_foreach('jsession')
    def test_get_bad_token_auth(self, server_info):
        server = xnatrest.Server(server_info['url'])
        resource = xnatrest.JsessionResource(server)
        response = resource.get(auth='bogus')
        print response.status
        self.assertEqual(response.status, 401, server_info['name'])
        return

    @config.test_foreach('jsession')
    def test_get_user_auth(self, server_info):
        server = xnatrest.Server(server_info['url'])
        resource = xnatrest.JsessionResource(server)
        response = resource.get(auth=('test1', 'test1'))
        self.assertEqual(response.status, 200, server_info['name'])
        return

    @config.test_foreach('jsession')
    def test_get_bad_user_auth(self, server_info):
        server = xnatrest.Server(server_info['url'])
        resource = xnatrest.JsessionResource(server)
        response = resource.get(auth=('test1', 'bogus'))
        self.assertEqual(response.status, 401, server_info['name'])
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
