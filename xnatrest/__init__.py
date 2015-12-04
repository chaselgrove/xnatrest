# See file COPYING distributed with xnatrest for copyright and license.

import urlparse
import httplib

from .exceptions import *
from . import resources

class HTTPHeaders:

    """class for storing HTTP response headers, supporting multiple values 
    for each header

    constructor is a list of 2-tuples (name, value)

    methods:

        items -- the list of 2-tuples

        get(name) -- get the first occurrence of the header

                     raises KeyError if the header is not found

                     h.get(name) is the same behavior as h[name]

        get_all(name) -- get a tuple of all occurrences of the header

    name comparisons are case-insensitive
    """

    def __init__(self, items):
        self.items = items
        return

    def __getitem__(self, key):
        key_l = key.lower()
        for (name, value) in self.items:
            if name.lower() == key_l:
                return value
        raise KeyError(key)

    def __contains__(self, key):
        key_l = key.lower()
        for (name, value) in self.items:
            if name.lower() == key_l:
                return True
        return False

    def get(self, name):
        return self[name]

    def get_all(self, key):
        values = []
        key_l = key.lower()
        for (name, value) in self.items():
            if name.lower() == key_l:
                values.append(value)
        if not values:
            raise KeyError(key)
        return values

class Response:

    """response object

    should not be instantiated directly by the user; use request() instead
    """

def request(server, method, rel_url=None, body='', headers={}):
    """request(server, method, rel_url=None, body='', headers={}) -> Response

    performs an HTTP request
    """
    if server.scheme == 'http':
        conn = httplib.HTTPConnection(server.netloc)
    else:
        conn = httplib.HTTPSConnection(server.netloc)
    try:
        if not rel_url:
            path = server.path
        else:
            path = server.path.rstrip('/') + rel_url
        conn.request(method, path, body, headers)
        response = conn.getresponse()
        status = response.status
        response_headers = HTTPHeaders(response.getheaders())
        data = response.read()
        msg = response.msg
    finally:
        conn.close()
    res = Response()
    res.server = server
    res.method = method
    res.rel_url = rel_url
    res.body = body
    res.request_headers = headers
    res.path = path
    res.status = status
    res.response_headers = response_headers
    res.data = data
    res.msg = msg
    return res

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
        res = request(server, 'GET')
        location = res.msg.getheader('Location')
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
        # 1.6.3 and 1.6.4 both return 'Unknown version' for the version
        # 1.6.3 will quote the header fields in CSV returns; 1.6.4 won't
        if self.version == 'Unknown version':
            r = self.request('GET', '/data/projects?format=csv')
            if r.status != 200:
                raise VersionError()
            header = r.data.split('\n')[0]
            if '"' in header:
                self.version = '1.6.3'
            else:
                self.version = '1.6.4'
        return

    def _get_jsessionid(self, auth=None):
        """_get_jsessionid(auth=None) -> JSESSIONID

        get a new JSESSIONID from the server

        If auth is given, it should be a (user, password) tuple.  If auth is 
        not given, no authorization is used.

        This method bypasses the authentication handling in 
        Connection.request() so should be used to set the connection 
        object's authentication mechanism (and only in this case).
        """
        if auth is None:
            headers = {}
        else:
            (user, password) = auth
            auth_string = self._generate_auth_string(user, password)
            headers = {'Authorization': auth_string}
        res = request(self.server, 'GET', headers=headers)
        cookie = res.msg.getheader('Set-Cookie')
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
        return request(self.server, method, rel_url, body, headers)

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
        res = request(self.server, 
                      'GET', 
                      headers={'Authorization': auth_string})
        if res.status == 401:
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
        return resources.ProjectsResource(self)

    def project(self, project_id):
        """project(project_id) -> project resource"""
        return resources.ProjectResource(self, project_id)

class Server:

    def __init__(self, url):
        self.url = url
        self._resolve_server(self.url, [])
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
        res = request(server, 'GET')
        location = res.msg.getheader('Location')
        if location:
            attempted_urls.append(url)
            self._resolve_server(location, attempted_urls)
            return
        self.parsed = server
        return

    def _detect_version(self):
        # 1.5 always requires a JSESSIONID, even for anonymous hits, so we 
        # hit the home page first to get a JSESSIONID before getting the 
        # version
        # "detect" since we might have to look at server quirks to get the 
        # actual version
        res = _request('GET', self.parsed, '/')
        cookie = res.msg.getheader('Set-Cookie')
        if not cookie or not cookie.startswith('JSESSIONID='):
            raise UnidentifiedServerError('no JSESSIONID returned')
        # get the session ID from "JSESSIONID=xxxxxxxxxxx" or 
        # "JSESSIONID=xxxxxxxxxx; ...other cookie stuff..."
        self.jsessionid = cookie.split(';')[0].strip()[11:]
        headers = {'Cookie': 'JSESSIONID=%s' % self.jsessionid}
        res = _request('GET', self.parsed, '/data/version', headers=headers)
        if res.status != 200:
            raise UnidentifiedServerError('could not get server version')
        self.version = res.data
        # 1.6.3 and 1.6.4 both return 'Unknown version' for the version
        # 1.6.3 will quote the header fields in CSV returns; 1.6.4 won't
        if self.version == 'Unknown version':
            res = _request('GET', self.parsed, '/data/projects?format=csv')
            if res.status != 200:
                raise UnidentifiedServerError('could not get server version')
            header = res.data.split('\n')[0]
            if '"' in header:
                self.version = '1.6.3'
            else:
                self.version = '1.6.4'
        return

def _request(method, server, rel_url=None, body='', headers={}):
    """_request(method, server, rel_url=None, body='', headers={}) -> Response

    performs an HTTP request
    """
    if server.scheme == 'http':
        conn = httplib.HTTPConnection(server.netloc)
    else:
        conn = httplib.HTTPSConnection(server.netloc)
    try:
        if not rel_url:
            path = server.path
        else:
            path = server.path.rstrip('/') + rel_url
        conn.request(method, path, body, headers)
        response = conn.getresponse()
        rv = Response()
        rv.status = response.status
        rv.headers = HTTPHeaders(response.getheaders())
        rv.data = response.read()
        rv.msg = response.msg
    finally:
        conn.close()
    return rv

# eof
