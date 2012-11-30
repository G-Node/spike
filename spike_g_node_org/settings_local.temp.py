# -*- coding: utf-8 -*-
#
# local django and pinax settings - extending the settings.py
#

from .settings import *

##---DEBUG

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SERVE_MEDIA = DEBUG

##---ADMIN-EMAILS

ADMINS = [
    # ("Your Name", "your_email@domain.com"),
]
MANAGERS = ADMINS
CONTACT_EMAIL = 'contact_email@project.com'

##---CSRF-TOKEN

SECRET_KEY = "change-this-to-something-with-more-entropy"

##---APPS

INSTALLED_APPS += [
    # project apps
    "taggit",
    "taggit_templatetags",
    "django_extensions",

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

##---ACCOUNT

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_USE_OPENID = False
ACCOUNT_REQUIRED_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = True
ACCOUNT_EMAIL_AUTHENTICATION = True
ACCOUNT_SIGNUP_REDIRECT_URL = "home"
ACCOUNT_LOGIN_REDIRECT_URL = "home"
ACCOUNT_LOGOUT_REDIRECT_URL = "home"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 2
ACCOUNT_UNIQUE_EMAIL = EMAIL_CONFIRMATION_UNIQUE_EMAIL = True

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG

##---EMAIL-SETTINGS

EMAIL_HOST = "localhost"
EMAIL_PORT = 25
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TSL = True
DEFAULT_FROM_EMAIL = "nopeply@spike.g-node.org"

##---MATPLOTLIB-BACKEND

import matplotlib

matplotlib.use('Agg')

##---EOF
