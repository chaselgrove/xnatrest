# See file COPYING distributed with xnatrest for copyright and license.

import unittest
import xnatrest

csv_header_1 = 'ID,secondary_ID,name,description,'
csv_header_2 = '"ID","secondary_ID","name","description",'

class TestProjects(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.central_c = xnatrest.Connection('https://central.xnat.org/')
        cls.nitrc_c = xnatrest.Connection('http://www.nitrc.org/ir/')
        cls.doi_c = xnatrest.Connection('http://doi.virtualbrain.org/xnat/')
        return

    def test_projects(self):
        for c in (self.central_c, self.nitrc_c, self.doi_c):
            resource = c.projects()
            response = resource.get(format='csv')
            d = response.data
            self.assertTrue(d.startswith(csv_header_1) \
                            or d.startswith(csv_header_2))
            self.assertEqual(response.status, 200)
        return

    def test_404(self):
        for c in (self.central_c, self.nitrc_c, self.doi_c):
            resource = c.project('bogus')
            response = resource.get()
            self.assertEqual(response.status, 404)
        return

# eof
