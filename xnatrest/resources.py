# See file COPYING distributed with xnatrest for copyright and license.

import urllib

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

# eof
