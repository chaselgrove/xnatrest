# See file COPYING distributed with xnatrest for copyright and license.

import urllib
import StringIO
import httplib
from .core import *

class BaseResource:

    def __init__(self, server):
        if not isinstance(server, Server):
            raise TypeError('server is not a Server instance')
        self.server = server
        return

    def _prep_args(self, auth, headers, body):
        """resource._prep_args(auth, headers, body) -> (headers, body)

        checks types for auth, headers, and body and raises TypeError as 
        appropriate

        auth is wrapped into the headers as needed

        headers is returned as a dictionary and body as a string
        """
        if headers is None:
            headers = {}
        elif not isinstance(headers, dict):
            raise TypeError('headers must be a dictionary or None')
        if isinstance(auth, basestring):
            headers['Cookie'] = 'JSESSIONID=%s' % auth
        elif auth is None:
            if self.server.version in ('1.5', '1.5.2', '1.5.3', '1.5.4', '1.6.2.1'):
                headers['Cookie'] = 'JSESSIONID=%s' % self.server._jsessionid
        else:
            raise TypeError('auth must be a basestring or None')
        if not isinstance(body, basestring):
            raise TypeError('body must be a basestring')
        return (headers, body)

    def _method_not_allowed(self, auth=None, headers=None, body=''):
        self._prep_args(auth, headers, body)
        response = Response()
        response.status = 405
        response.headers = httplib.HTTPMessage(StringIO.StringIO())
        response.data = ''
        return response

    head = _method_not_allowed
    get = _method_not_allowed
    put = _method_not_allowed
    post = _method_not_allowed
    delete = _method_not_allowed

class JsessionResource(BaseResource):

    def get(self, auth=None, headers=None, body=''):
        (headers, body) = self._prep_args(auth, headers, body)
        response = self.server._request('GET', '/data/JSESSION', headers)
        return response

# eof
