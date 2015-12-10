# See file COPYING distributed with xnatrest for copyright and license.

from .. import Response
from .base import BaseResource

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
