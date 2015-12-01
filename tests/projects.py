# See file COPYING distributed with xnatrest for copyright and license.

import unittest
from . import config
import xnatrest

csv_header_1 = 'ID,secondary_ID,name,description,'
csv_header_2 = '"ID","secondary_ID","name","description",'

class TestProjects(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.servers = []
        for server in config.servers:
            d = dict(server)
            d['connection'] = xnatrest.Connection(server['url'])
            cls.servers.append(d)
        return

    def test_projects(self):
        for server in self.servers:
            print server['name']
            resource = server['connection'].projects()
            response = resource.get(format='csv')
            d = response.data
            self.assertTrue(d.startswith(csv_header_1) \
                            or d.startswith(csv_header_2), 
                            server['name'])
            self.assertEqual(response.status, 200, server['name'])
        return

    def test_404(self):
        for server in self.servers:
            print server['name']
            resource = server['connection'].project('bogus')
            response = resource.get()
            self.assertEqual(response.status, 404, server['name'])
        return

# eof
