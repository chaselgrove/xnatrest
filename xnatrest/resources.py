# See file COPYING distributed with xnatrest for copyright and license.

import urllib
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
        auth_msg = 'auth must be a basestring, a two-tuple of strings, or None'
        if isinstance(auth, basestring):
            headers['Cookie'] = 'JSESSIONID=%s' % auth
        elif isinstance(auth, (list, tuple)):
            if len(auth) != 2:
                raise ValueError(auth_msg)
            up_string = '%s:%s' % tuple(auth)
            auth_string = 'Basic %s' % up_string.encode('base64')
            auth_string = auth_string.replace('\n', '')
            headers['Authorization'] = auth_string
        elif auth is None:
            if self.server.version in ('1.5', 
                                       '1.5.2', 
                                       '1.5.3', 
                                       '1.5.4', 
                                       '1.6.2.1'):
                headers['Cookie'] = 'JSESSIONID=%s' % self.server._jsessionid
        else:
            raise TypeError(auth_msg)
        if not isinstance(body, basestring):
            raise TypeError('body must be a basestring')
        return (headers, body)

    def _method_not_allowed(self, auth=None, headers=None, body=''):
        self._prep_args(auth, headers, body)
        response = Response(405)
        return response

    head = _method_not_allowed
    get = _method_not_allowed
    put = _method_not_allowed
    post = _method_not_allowed
    delete = _method_not_allowed

class JsessionResource(BaseResource):

    def get(self, auth=None, headers=None, body=''):
        if isinstance(auth, basestring):
            session_token = auth
        else:
            session_token = None
        (headers, body) = self._prep_args(auth, headers, body)
        response = self.server._request('GET', '/data/JSESSION', headers)
        # 1.6.3-1.6.5 returns 200 if a bad JSESSIONID is passed; fix this to 
        # 401 (we know this has happened when the returned session identifier 
        # differs from the passed one
        if self.server.version in ('1.6.3', '1.6.4', '1.6.5'):
            if session_token is not None and session_token != response.data:
                response = Response(401)
        return response

    post = get

    def delete(self, auth=None, headers=None, body=''):
        if auth is None:
            response = Response(401)
        if isinstance(auth, basestring):
            session_token = auth
        else:
            session_token = None
        (headers, body) = self._prep_args(auth, headers, body)
        response = self.server._request('GET', '/data/JSESSION', headers)
        # 1.6.3, 1.6.4, and 1.6.5 return 200 (and a set-cookie JSESSIONID) if 
        # a bad session was passed
        # catch that here and return 401
        if self.server.version in ('1.6.3', '1.6.4', '1.6.5'):
            if session_token is not None:
                if 'JSESSIONID' in response.cookies:
                    if session_token != response.cookies['JSESSIONID']:
                        response = Response(401)
        return response

# eof
