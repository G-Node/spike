# -*- coding: utf-8 -*-
#
# django settings for G-Node project.
# adjusted for spikesorting evaluation website
#
# 2012/05/23 Philipp Meier <pmeier82@googlemail.com>
#

##---GENERAL

from .general import *

##---LOCAL

try:
    from .local import *
except ImportError:
    pass

##---CELERY

try:
    from .celery import *
except ImportError:
    pass
