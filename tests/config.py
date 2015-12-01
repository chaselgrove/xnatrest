# See file COPYING distributed with xnatrest for copyright and license.

import ConfigParser

config = ConfigParser.ConfigParser()
config.read('tests.cfg')

non_xnat_url = config.get('non-xnat', 'url')

servers = []

for section in config.sections():
    if not config.has_option(section, 'url'):
        continue
    if not config.has_option(section, 'version'):
        continue
    servers.append({'name': section, 
                    'url': config.get(section, 'url'), 
                    'version': config.get(section, 'version')})

# eof
