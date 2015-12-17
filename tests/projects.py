# See file COPYING distributed with xnatrest for copyright and license.

import unittest
from . import config
#from . import generate_identifier
import xnatrest

class TestProjectsGet(unittest.TestCase):

    @config.test_foreach('projects')
    def test_get_noauth(self, server_info):
        server = xnatrest.Server(server_info['url'])
        resource = xnatrest.ProjectsResource(server)
        response = resource.get()
        self.assertEqual(response.status, 200, server_info['name'])
        return

    @config.test_foreach('projects')
    def test_get_user_auth(self, server_info):
        server = xnatrest.Server(server_info['url'])
        resource = xnatrest.ProjectsResource(server)
        response = resource.get(auth=('test1', 'test1'))
        self.assertEqual(response.status, 200, server_info['name'])
        return

    @config.test_foreach('projects')
    def test_get_bad_user_auth(self, server_info):
        server = xnatrest.Server(server_info['url'])
        resource = xnatrest.ProjectsResource(server)
        response = resource.get(auth=('test1', 'bogus'))
        self.assertEqual(response.status, 401, server_info['name'])
        return

    @config.test_foreach('projects')
    def test_get_token_auth(self, server_info):
        server = xnatrest.Server(server_info['url'])
        resource = xnatrest.ProjectsResource(server)
        response = resource.get()
        self.assertEqual(response.status, 200, server_info['name'])
        return

#class TestProjectsPost(unittest.TestCase):
#
#    @config.test_foreach('projects')
#    def test_post(self, server_info):
#        print generate_identifier()
#        self.assertEqual(1,2)
#        return

class TestProjectsPut(unittest.TestCase):

    @config.test_foreach('projects')
    def test_put(self, server_info):
        server = xnatrest.Server(server_info['url'])
        resource = xnatrest.ProjectsResource(server)
        response = resource.put(auth=('test1', 'test1'))
        self.assertEqual(response.status, 405, server_info['name'])
        return

class TestProjectsDelete(unittest.TestCase):

    @config.test_foreach('projects')
    def test_delete(self, server_info):
        server = xnatrest.Server(server_info['url'])
        resource = xnatrest.ProjectsResource(server)
        response = resource.delete(auth=('test1', 'test1'))
        self.assertEqual(response.status, 405, server_info['name'])
        return

# eof
