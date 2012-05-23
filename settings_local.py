# -*- coding: utf-8 -*-
#
# local server django settings for G-Node project.
# adjusted for spikesorting evaluation website
#
# 2012/05/23 Philipp Meier <pmeier82@googlemail.com>
#

##---IMPORTS

import os
import pinax

##---GENERAL

PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

SITE_NAME = 'G-Node'
ROOT_URLCONF = 'urls'
PINAX_THEME = 'default'
USE_I18N = False

SERVE_MEDIA = True
PRODUCTION_MODE = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = '0osjm6r8sb(+y@b)oy4&h=8(ge-!ckn$1p$9#6yabukc_e%9gi'

##---DATABASES

DATABASES = {
    'default':{
        'ENGINE':'django.db.backends.mysql',
        'HOST':'127.0.0.1',
        'PORT':'33306',
        'NAME':'g-node-spike',
        'USER':'portal',
        'PASSWORD':'pass',
        'TIME_ZONE':'Europe/Berlin',
        },
    }

##---PATHS

TMP_FILES_PATH = '/tmp/'

# media files
# Absolute path to the directory that holds PUBLIC media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/data/public_media/'
MEDIA_URL = '/site_media/media/'

# file media - user files
FILE_MEDIA_ROOT = '/data/private_media/'

# static files
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'static')
STATIC_URL = '/site_media/static/'

# Additional directories which hold static files
# XXX: doesn't look correct
STATICFILES_DIRS = (
    ('g-node-portal', os.path.join(PROJECT_ROOT, 'media')),
    ('pinax', os.path.join(PINAX_ROOT, 'media', PINAX_THEME)),
    )

ADDED_URL = ''

##---ACCOUNTS

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_REQUIRED_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = False

##---AUTH

# LDAP configuration
AUTHENTICATION_BACKENDS = (
    'ldap_backend.models.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
    )
AUTH_LDAP_SWITCHED_ON = True
AUTH_LDAP_SERVER = 'gate.g-node.org'            # Hostname if in the web
#AUTH_LDAP_SERVER = 'dstest.g-node.pri'			# Hostname if inside
# G-Node network
AUTH_LDAP_BASE_USER = 'cn=Directory Manager'        # Administrative User's
# Username
AUTH_LDAP_BASE_PASS = 'xEkl91Q'                # Administrative User's Password
AUTH_LDAP_BASE_DN = 'o=g-node.org,o=g-node'        # Base DN (also accepts
# o=example.com format)
AUTH_LDAP_FIELD_DOMAIN = 'g-node.pri'            # Domain from which users
# will take the domain for dummy e-mail generation (it keeps Django happy!)
AUTH_LDAP_GROUP_NAME = 'ldap_people'            # Django group for LDAP
# users (helps us manage them for password changing, etc.)
AUTH_LDAP_VERSION = 3                    # LDAP version
AUTH_LDAP_OLDPW = True                    # Can the server take the old
# password? True/False

# Optional
AUTH_LDAP_FIELD_USERAUTH = 'uid'            # The field from which the user
# authentication shall be done.
AUTH_LDAP_FIELD_AUTHUNIT = 'People'            # The organisational unit in
# which your users shall be found.
AUTH_LDAP_FIELD_USERNAME = 'uid'            # The field from which to draw
# the username (Default 'uid'). (Allows non-uid/non-dn custom fields to be
# used for login.)
AUTH_LDAP_WITHDRAW_EMAIL = True            # Should django try the directory
# for the user's email ('mail')? True/False.

##---EMAIL

EMAIL_HOST = 'mx1.g-node.org'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'support'
EMAIL_HOST_PASSWORD = '82uKmNqr'
EMAIL_USE_TLS = False
EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG
CONTACT_EMAIL = 'support@portal.g-node.org'
DEFAULT_FROM_EMAIL = 'support@'

##---THRESHOLDS

MAX_REGISTR_FROM_IP_DAILY = 20
MAX_FILE_PROCESSING_SIZE = 20971520 # in bytes
MAX_DATAPOINTS_DISPLAY = 300

##---AVATARS

AVATAR_GRAVATAR_BACKUP = False
AVATAR_DEFAULT_URL = os.path.join(
    STATIC_URL, 'pinax/images/avatar_default.jpeg')


##---CELERY

try:
    import djcelery

    djcelery.setup_loader()

    # celery task broker settings
    BROKER_HOST = 'localhost'
    BROKER_PORT = 5672
    BROKER_USER = 'portal'
    BROKER_PASSWORD = 'pass'
    BROKER_VHOST = 'localhost'

    # celery task broker result storage settings.
    CELERY_RESULT_BACKEND = 'database'
    CELERY_RESULT_DBURI = 'mysql://portal:pass@localhost:33306/g-node-spike'
except ImportError:
    pass
