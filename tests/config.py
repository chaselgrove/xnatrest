# See file COPYING distributed with xnatrest for copyright and license.

import ConfigParser

known_tests = ('non-xnat', 'version', 'jsession')

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

aliases = {}
if config.has_section('aliases'):
    for (alias, tests) in config.items('aliases'):
        aliases[alias] = []
        for test in [ el.strip() for el in tests.split(',') ]:
            if test not in known_tests:
                raise ValueError('unknown test "%s"' % test)
            aliases[alias].append(test)

tests = {}

for server_name in config.sections():
    if server_name == 'aliases':
        continue
    server = dict(config.items(server_name))
    server['name'] = server_name
    if 'tests' not in server:
        raise KeyError('config section %s has no tests option' % server)
    if 'url' not in server:
        raise KeyError('config section %s has no url option' % server)
    server_tests = set()
    for test in [ el.strip() for el in server['tests'].split(',') ]:
        if test in aliases:
            server_tests.update(aliases[test])
        elif test in known_tests:
            server_tests.add(test)
        else:
            raise ValueError('unknown test "%s"' % test)
    for test in server_tests:
        tests.setdefault(test, []).append(server)

if __name__ == '__main__':
    for test in tests:
        print test
        for server in tests[test]:
            print '    %s' % server['name']

# eof
