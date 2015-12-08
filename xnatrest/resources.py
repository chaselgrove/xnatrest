# See file COPYING distributed with xnatrest for copyright and license.

import urllib
from .core import *

class BaseResource:

    def __init__(self, server):
        if not isinstance(server, Server):
            raise TypeError('server is not a Server instance')
        self.server = server
        return

    def _method_not_allowed(self, auth=None, headers={}, body=''):
        response = Response()
        response.status = 405
        response.headers = HTTPHeaders()
        response.data = ''
        return response

    head = _method_not_allowed
    get = _method_not_allowed
    put = _method_not_allowed
    post = _method_not_allowed
    delete = _method_not_allowed

class JsessionResource(BaseResource):

    def get(self, auth=None, headers=None, body=''):
        if not headers:
            headers = {}
        if self.server.version in ('1.5', '1.5.2', '1.5.3', '1.5.4', '1.6.2.1'):
            if not 'Cookie' in headers \
                or not headers['Cookie'].startswith('JSESSIONID='):
                headers['Cookie'] = 'JSESSIONID=%s' % self.server._jsessionid
        response = self.server._request('GET', '/data/JSESSION', headers)
        return response

"""

class BaseResource:

    def __init__(self, connection):
        self.connection = connection
        return

class ProjectsResource(BaseResource):

    def get(self, format=None):
        params = {}
        if format is not None:
            if format not in ('html', 'json', 'xml', 'csv'):
                raise ValueError('bad value for format')
            params['format'] = format
        url = '/data/archive/projects'
        if params:
            url = '%s?%s' % (url, urllib.urlencode(params))
        return self.connection.request('GET', url)

class ProjectResource(BaseResource):

    def __init__(self, connection, project_id):
        BaseResource.__init__(self, connection)
        self.project_id = project_id
        return

    def get(self, format=None):
        params = {}
        if format is not None:
            if format not in ('html', 'json', 'xml'):
                raise ValueError('bad value for format')
            params['format'] = format
        url = '/data/archive/projects/%s' % self.project_id
        if params:
            url = '%s?%s' % (url, urllib.urlencode(params))
        return self.connection.request('GET', url)
"""

# eof
