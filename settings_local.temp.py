# -*- coding: utf-8 -*-
#
# local django and pinax settings - extending the settings.py
#

from settings import *

##---DEBUG

DEBUG = False
TEMPLATE_DEBUG = DEBUG
SERVE_MEDIA = DEBUG
COMPRESS = False

##---ADMIN-EMAILS

ADMINS = [
    # ("Your Name", "your_email@domain.com"),
]
MANAGERS = ADMINS

##---DATABASE

DATABASES = {
    "default":{
        "ENGINE":"django.db.backends.mysql",
        "NAME":"db-name",
        "USER":"db-user",
        "PASSWORD":"db-user-pass",
        "HOST":"",
        "PORT":"",
        }
}

##---LANGUAGE-AND-LOCALE

TIME_ZONE = "Europe/Berlin"
LANGUAGE_CODE = "en-gb"
USE_I18N = True

# restrict available language choices
gettext_noop = lambda s:s
LANGUAGES = (
    ('de', gettext_noop('German')),
    ('en', gettext_noop('English')),
    ('es', gettext_noop('Spanish')),
    ('fr', gettext_noop('French')),
    ('it', gettext_noop('Italian')),
    )

##---FILE-PATHS

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media", "media")
STATIC_ROOT = os.path.join(PROJECT_ROOT, "site_media", "static")
FILE_UPLOAD_PERMISSIONS = 0644

##---CSRF-TOKEN

SECRET_KEY = "yh@yy^c#yqdeh(0ukoz-f@ft)=c%&0!uz7)mi0=48#v=laq6x7"

##---APPS

INSTALLED_APPS += [
    # project apps
]

MIDDLEWARE_CLASSES += [
    # project middleware
]

##---ACCOUNT

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_USE_OPENID = True
ACCOUNT_REQUIRED_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = True
ACCOUNT_EMAIL_AUTHENTICATION = False
ACCOUNT_UNIQUE_EMAIL = EMAIL_CONFIRMATION_UNIQUE_EMAIL = False

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG

##---EMAIL-SETTINGS

EMAIL_HOST = "localhost"
EMAIL_PORT = 25
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TSL = False
