# See file COPYING distributed with xnatrest for copyright and license.

import urlparse
import httplib

from .exceptions import *

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

    def __init__(self, items=[]):
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

    def __str__(self):
        return '<Response %d>' % self.status

class Server:

    def __init__(self, url):
        self.url = url
        self._resolve_server(self.url, [])
        self._detect_version()
        return

    def __str__(self):
        return '<Server %s (%s)>' % (self.url, self.version)

    def _resolve_server(self, url, attempted_urls):
        # resolve the actual location of the server (let the server redirect 
        # to HTTPS, append a trailing slash, etc)
        if url in attempted_urls:
            raise CircularReferenceError(url)
        self.parsed = urlparse.urlparse(url)
        if self.parsed.scheme not in ('http', 'https'):
            raise ValueError('unsupported scheme "%s"' % self.parsed.scheme)
        if not self.parsed.netloc:
            raise ValueError('no server given')
        res = self._request('GET', '/')
        location = res.msg.getheader('Location')
        if location:
            attempted_urls.append(url)
            self._resolve_server(location, attempted_urls)
            return
        return

    def _detect_version(self):
        # 1.5 always requires a JSESSIONID, even for anonymous hits, so we 
        # hit the home page first to get a JSESSIONID before getting the 
        # version
        # "detect" since we might have to look at server quirks to get the 
        # actual version
        res = self._request('GET', '/')
        cookie = res.msg.getheader('Set-Cookie')
        if not cookie or not cookie.startswith('JSESSIONID='):
            raise UnidentifiedServerError('no JSESSIONID returned')
        # get the session ID from "JSESSIONID=xxxxxxxxxxx" or 
        # "JSESSIONID=xxxxxxxxxx; ...other cookie stuff..."
        self._jsessionid = cookie.split(';')[0].strip()[11:]
        headers = {'Cookie': 'JSESSIONID=%s' % self._jsessionid}
        res = self._request('GET', '/data/version', headers=headers)
        if res.status == 404:
            self.version = '1.5'
            return
        if res.status != 200:
            raise UnidentifiedServerError('could not get server version')
        self.version = res.data
        # 1.6.3 and 1.6.4 both return 'Unknown version' for the version
        # 1.6.3 will quote the header fields in CSV returns; 1.6.4 won't
        if self.version != 'Unknown version':
            return
        res = self._request('GET', '/data/projects?format=csv')
        if res.status != 200:
            raise UnidentifiedServerError('could not get server version')
        header = res.data.split('\n')[0]
        if '"' in header:
            self.version = '1.6.3'
        else:
            self.version = '1.6.4'
        return

    def _request(self, method, rel_url=None, headers={}, body=''):
        if self.parsed.scheme == 'http':
            conn = httplib.HTTPConnection(self.parsed.netloc)
        else:
            conn = httplib.HTTPSConnection(self.parsed.netloc)
        try:
            if not rel_url:
                path = self.parsed.path
            else:
                path = self.parsed.path.rstrip('/') + rel_url
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
