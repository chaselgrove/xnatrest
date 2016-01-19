# See file COPYING distributed with xnatrest for copyright and license.

from .. import Response
from .base import BaseResource

content_type_body = """Supported content-types are:
    text/html
    text/csv
    text/xml
    application/xml
    application/json
"""

class ProjectsResource(BaseResource):

    def get(self, auth=None, headers=None, body=''):
        if isinstance(auth, basestring):
            session_token = auth
        else:
            session_token = None
        (headers, body) = self._prep_args(auth, headers, body)
        if 'content-type' in headers:
            if headers['content-type'] == 'text/html':
                url = '/data/projects?format=html'
            elif headers['content-type'] == 'text/csv':
                url = '/data/projects?format=csv'
            elif headers['content-type'] in ('text/xml', 'application/xml'):
                url = '/data/projects?format=xml'
            elif headers['content-type'] == 'application/json':
                url = '/data/projects?format=json'
            else:
                return Response(406, 
                                {'Content-Type': 'text/plain'}, 
                                content_type_body)
            del headers['content-type']
        else:
            url = '/data/projects'
        response = self.server._request('GET', url, headers)
        # content-type: application/vnd.ms-excel -> text/csv 
        # for some 1.5 series XNATs
        if self.server.version in ('1.5', '1.5.2', '1.5.3', '1.5.4'):
            if 'content-type' in response.headers:
                ct = response.headers['content-type']
                if ct == 'application/vnd.ms-excel':
                    response.headers['content-type'] = 'text/csv'
        return response

    def post(self, auth=None, headers=None, body=''):
        raise NotImplementedError()

# eof
