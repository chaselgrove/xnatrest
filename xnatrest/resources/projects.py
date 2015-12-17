# See file COPYING distributed with xnatrest for copyright and license.

from .. import Response
from .base import BaseResource

class ProjectsResource(BaseResource):

    def get(self, auth=None, headers=None, body=''):
        if isinstance(auth, basestring):
            session_token = auth
        else:
            session_token = None
        (headers, body) = self._prep_args(auth, headers, body)
        response = self.server._request('GET', '/data/projects', headers)
        return response

    def post(self, auth=None, headers=None, body=''):
        raise NotImplementedError()

# eof
