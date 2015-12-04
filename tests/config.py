# See file COPYING distributed with xnatrest for copyright and license.

import ConfigParser

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
