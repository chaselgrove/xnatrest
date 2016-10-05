# See file COPYING distributed with xnatrest for copyright and license.

class XNATRESTError(Exception):

    """base class for xnatrest exceptions"""

class CircularReferenceError(XNATRESTError):

    def __init__(self, url):
        self.url = url
        return

    def __str__(self):
        return 'circular reference to %s' % self.url

class UnidentifiedServerError(XNATRESTError):

    def __str__(self):
        return 'could not identify server'

# eof
