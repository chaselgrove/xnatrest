# See file COPYING distributed with xnatrest for copyright and license.

import nose.tools
import xnatrest

def connect_to_non_xnat():
    c = xnatrest.Connection('http://www.nitrc.org')
    return

def bad_auth():
    c = xnatrest.Connection('https://central.xnat.org/')
    c.auth_user_password('nosetests', 'bogus')
    return

def test_redirect():
    c = xnatrest.Connection('http://central.xnat.org')
    assert c.server.scheme == 'https'
    assert c.server.netloc == 'central.xnat.org'
    assert c.server.path == '/'
    return

def test_version():
    c = xnatrest.Connection('http://www.nitrc.org/ir')
    assert c.version == '1.5.4'
    return

def test_nojsessionid():
    nose.tools.assert_raises(xnatrest.JSESSIONIDError, connect_to_non_xnat)
    return

def test_bad_auth():
    nose.tools.assert_raises(xnatrest.AuthenticationError, bad_auth)
    return

def test_auth():
    c = xnatrest.Connection('https://central.xnat.org/')
    assert c.auth_type == 'jsessionid'
    assert c.user is None
    c.auth_jsessionid('nosetests', 'nose')
    assert c.auth_type == 'jsessionid'
    assert c.user == 'nosetests'
    c.auth_anonymous()
    assert c.auth_type == 'jsessionid'
    assert c.user is None
    jsessionid = c._jsessionid
    c.auth_anonymous()
    assert c._jsessionid != jsessionid
    return

# eof
