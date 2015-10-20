# See file COPYING distributed with xnatrest for copyright and license.

import urlparse
import httplib

from .exceptions import *
from . import resources

class _Request:

    def __init__(self, 
                 server, 
                 method, 
                 rel_url=None, 
                 body='', 
                 headers={}):
        self.server = server
        self.method = method
        self.rel_url = rel_url
        self.body = body
        self.request_headers = headers
        if self.server.scheme == 'http':
            conn = httplib.HTTPConnection(self.server.netloc)
        else:
            conn = httplib.HTTPSConnection(self.server.netloc)
        try:
            if not self.rel_url:
                self.path = self.server.path
            else:
                self.path = server.path.rstrip('/') + rel_url
            conn.request(self.method, 
                         self.path, 
                         self.body, 
                         self.request_headers)
            response = conn.getresponse()
            self.status = response.status
            self.response_headers = response.getheaders()
            self.data = response.read()
            self.msg = response.msg
        finally:
            conn.close()
        return

class Connection:

    def __init__(self, url):
        self.url = url
        self._resolve_server(url, [])
        self.auth_type = 'jsessionid'
        self.user = None
        self._auth_string = None
        self._jsessionid = self._get_jsessionid()
        self._detect_version()
        return

    def _resolve_server(self, url, attempted_urls):
        # resolve the actual location of the server (let the server redirect 
        # to HTTPS, append a trailing slash, etc)
        if url in attempted_urls:
            raise CircularReferenceError(url)
        server = urlparse.urlparse(url)
        if server.scheme not in ('http', 'https'):
            raise ValueError('unsupported scheme "%s"' % server.scheme)
        if not server.netloc:
            raise ValueError('no server given')
        r = _Request(server, 'GET')
        location = r.msg.getheader('Location')
        if location:
            attempted_urls.append(url)
            self._resolve_server(location, attempted_urls)
        else:
            self.server = server
        return

    def _detect_version(self):
        # 1.5 always requires a JSESSIONID, even for anonymous hits, so we 
        # hit the home page first to get a JSESSIONID before getting the 
        # version
        # "detect" since we might have to look at server quirks to get the 
        # actual version
        r = self.request('GET', '/data/version')
        if r.status != 200:
            raise VersionError()
        self.version = r.data
        return

    def _get_jsessionid(self, auth=None):
        """_get_jsessionid(auth=None) -> JSESSIONID

        get a new JSESSIONID from the server

        If auth is given, it should be a (user, password) tuple.  If auth is 
        not given, no authorization is used.

        This method bypasses the authentication handling in request() so 
        should be used to set the connection object's authentication 
        mechanism (and only in this case).
        """
        if auth is None:
            headers = {}
        else:
            (user, password) = auth
            auth_string = self._generate_auth_string(user, password)
            headers = {'Authorization': auth_string}
        r = _Request(self.server, 'GET', headers=headers)
        cookie = r.msg.getheader('Set-Cookie')
        if not cookie or not cookie.startswith('JSESSIONID='):
            raise JSESSIONIDError()
        # cooke is: JSESSIONID=...........; <other cookie stuff>
        return cookie.split(';')[0][11:]

    def _generate_auth_string(self, user, password):
        up_string = '%s:%s' % (user, password)
        auth_string = 'Basic %s' % up_string.encode('base64')
        auth_string = auth_string.replace('\n', '')
        return auth_string

    def request(self, method, rel_url=None, body='', headers={}):
        if self.auth_type == 'jsessionid':
            headers['Cookie'] = 'JSESSIONID=%s' % self._jsessionid
        elif self.auth_type == 'user/password':
            headers['Authorization'] = self._auth_string
        else:
            assert False
        return _Request(self.server, method, rel_url, body, headers)

    def auth_anonymous(self):
        # log in before logging out in case there's a problem on login
        new_jsessionid = self._get_jsessionid()
        if self.auth_type == 'jsessionid':
            self.request('DELETE', '/data/JSESSION')
        elif self.auth_type == 'user/password':
            pass
        else:
            assert False
        self.auth_type = 'jsessionid'
        self.user = None
        self._auth_string = None
        self._jsessionid = new_jsessionid
        return

    def auth_user_password(self, user, password):
        # log in before logging out in case there's a problem on login
        # check the authorization with a simple hit first
        auth_string = self._generate_auth_string(user, password)
        r = _Request(self.server, 'GET', headers={'Authorization': auth_string})
        if r.status == 401:
            raise AuthenticationError()
        if self.auth_type == 'jsessionid':
            self.request('DELETE', '/data/JSESSION')
        elif self.auth_type == 'user/password':
            pass
        else:
            assert False
        self.auth_type = 'user/password'
        self.user = user
        self._auth_string = auth_string
        self._jsessionid = None
        return

    def auth_jsessionid(self, user, password):
        # log in before logging out in case there's a problem on login
        new_jsessionid = self._get_jsessionid((user, password))
        if self.auth_type == 'jsessionid':
            self.request('DELETE', '/data/JSESSION')
        elif self.auth_type == 'user/password':
            pass
        else:
            assert False
        self.auth_type = 'jsessionid'
        self.user = user
        self._auth_string = None
        self._jsessionid = new_jsessionid
        return

    def projects(self):
        """projects() -> projects resource"""
        return resources._ProjectsResource(self)

# eof
