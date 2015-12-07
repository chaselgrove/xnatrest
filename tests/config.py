# See file COPYING distributed with xnatrest for copyright and license.

import ConfigParser

class test_foreach:

    """decorator for looping over test servers

    the following will check for a 'non-xnat' section in tests

        @test_foreach('non-xnat')
        def test_non_xnat(self, server):
            ...

    if the section exists, the servers in this section will be passed 
    to the test function

    if the section does not exist, the test is skipped

    note that the decorator changes the signature of the method from 
    test(self, sever) to test(self), which is what unittest expects
    """

    def __init__(self, test_type):
        self.test_type = test_type
        return

    def __call__(self, f0):
        def f(instance):
            if self.test_type not in tests:
                msg = 'no %s servers declared in config' % self.test_type
                instance.skipTest(msg)
            for server in tests[self.test_type]:
                f0(instance, server)
        return f

config = ConfigParser.ConfigParser()
config.read('tests.cfg')

tests = {}

for server_name in config.sections():
    server = dict(config.items(server_name))
    server['name'] = server_name
    if 'tests' not in server:
        raise KeyError('config section %s has no tests option' % server)
    if 'url' not in server:
        raise KeyError('config section %s has no url option' % server)
    for test in server['tests'].split(','):
        if test == 'non-xnat':
            pass
        elif test == 'version':
            pass
        else:
            raise ValueError('unknown test "%s"' % test)
        tests.setdefault(test, []).append(server)

# eof
