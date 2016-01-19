# See file COPYING distributed with xnatrest for copyright and license.

import urlparse
import httplib
import StringIO

from .exceptions import *

class Response:

    """response object

    should not be instantiated directly by the user; use request() instead
    """

    def __init__(self, status, headers=None, data=''):
        self.status = status
        if isinstance(headers, httplib.HTTPMessage):
            self.headers = headers
        else:
            self.headers = httplib.HTTPMessage(StringIO.StringIO())
            if headers is not None:
                for key in headers:
                    self.headers[key] = headers[key]
        self.cookies = {}
        for header in self.headers.getallmatchingheaders('set-cookie'):
            header_value = header[12:]
            cookie = header_value.split(';')[0].strip()
            try:
                (name, value) = cookie.split('=', 1)
                self.cookies[name] = value
            except ValueError:
                pass
        self.data = data
        return

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
        location = res.headers.getheader('Location')
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
        cookie = res.headers.getheader('Set-Cookie')
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
            rv = Response(response.status, response.msg, response.read())
        finally:
            conn.close()
        return rv

# eof
