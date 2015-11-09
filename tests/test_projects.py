# See file COPYING distributed with xnatrest for copyright and license.

import nose.tools
import xnatrest

csv_header_1 = 'ID,secondary_ID,name,description,'
csv_header_2 = '"ID","secondary_ID","name","description",'

def setup():
    global central_c
    global nitrc_c
    global doi_c
    central_c = xnatrest.Connection('https://central.xnat.org/')
    nitrc_c = xnatrest.Connection('http://www.nitrc.org/ir/')
    doi_c = xnatrest.Connection('http://doi.virtualbrain.org/xnat/')
    return

def test_projects():
    for c in (central_c, nitrc_c, doi_c):
        resource = c.projects()
        response = resource.get(format='csv')
        d = response.data
        assert d.startswith(csv_header_1) or d.startswith(csv_header_2)
        assert response.status == 200
    return

def test_404():
    for c in (central_c, nitrc_c, doi_c):
        resource = c.project('bogus')
        response = resource.get()
        assert response.status == 404
    return

# eof
