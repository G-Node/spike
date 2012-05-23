# -*- coding: utf-8 -*-
#
# django settings for G-Node project.
# adjusted for spikesorting evaluation website
#
# 2012/05/23 Philipp Meier <pmeier82@googlemail.com>
#

##---GENERAL

from config.general import *

##---LOCAL

from config.local import *

##---CELERY

try:
    from celeryconfig import *
except ImportError, e:
    print e
