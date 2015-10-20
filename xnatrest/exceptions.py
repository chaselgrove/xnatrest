# See file COPYING distributed with xnatrest for copyright and license.

class XNATRESTError(Exception):

    """base class for llxnat exceptions"""

class CircularReferenceError(XNATRESTError):

    def __init__(self, url):
        self.url = url
        return

    def __str__(self):
        return 'circular reference to %s' % self.url

class VersionError(XNATRESTError):

    def __str__(self):
        return 'could not get version'

class JSESSIONIDError(XNATRESTError):

    def __str__(self):
        return 'error getting JSESSIONID'

class AuthenticationError(XNATRESTError):

    def __str__(self):
        return 'error in authentication'

# eof
