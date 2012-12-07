# -*- coding: utf-8 -*-
#
# local django and pinax settings - extending the settings.py
#

from .settings import *

##---DEBUG

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SERVE_MEDIA = DEBUG

##---SITE-SPECIFIC

ADMINS = [
    # ("Your Name", "your_email@domain.com"),
]
MANAGERS = ADMINS
CONTACT_EMAIL = "contact_email@project.com"

SECRET_KEY = "change-this-to-something-with-more-entropy"

##---APPS

INSTALLED_APPS += [
    # project apps
    "taggit",
    "taggit_templatetags",
    "django_extensions",
    "crontab",

    # spike core
    "spike",
    "spike.algorithm",
    "spike.benchmark",
    "spike.evaluation",
    "spike.data",
    "spike.log",

    # spike modules
    "spike.module",
    "spike.module.default_visual",
    "spike.module.metric_ffranke",
]

##---EMAIL

EMAIL_BACKEND = "mailer.backend.DbBackend"

EMAIL_HOST = "localhost"
EMAIL_PORT = 25
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TSL = True

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG

DEFAULT_FROM_EMAIL = "nopeply@spike.g-node.org"
SERVER_EMAIL = DEFAULT_FROM_EMAIL

##---ACCOUNT

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True
ACCOUNT_EMAIL_CONFIRMATION_EMAIL = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

##---EMAIL-SETTINGS

EMAIL_HOST = "localhost"
EMAIL_PORT = 25
#EMAIL_HOST_USER = ""
#EMAIL_HOST_PASSWORD = ""
#EMAIL_USE_TSL = True
#DEFAULT_FROM_EMAIL = "Spikesorting Evaluation <nopeply@spike.g-node.org>"
#SERVER_EMAIL = DEFAULT_FROM_EMAIL

##---MATPLOTLIB-BACKEND

import matplotlib

matplotlib.use('Agg')

##---EOF
