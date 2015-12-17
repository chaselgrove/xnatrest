# See file COPYING distributed with xnatrest for copyright and license.

import random

from .server import *
from .jsession import *

def generate_identifier():
    return '%08x' % random.getrandbits(32)

# eof
