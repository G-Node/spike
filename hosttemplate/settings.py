# -*- coding: utf-8 -*-
#
# general django settings
#
# do no not edit! instead edit settings_local.py, settings_db.py and settings_celery.py
#

##---IMPORTS

import os

##---PROJECT-SETTINGS

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SITE_ID = 1
INTERNAL_IPS = ["127.0.0.1"]

ADMINS = []
MANAGERS = ADMINS

SECRET_KEY = "change-this-to-something-with-more-entropy"

##---DATABASE

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "db-name",
        "USER": "db-user",
        "PASSWORD": "db-user-pass",
        "HOST": "",
        "PORT": "",
    }
}

##---CACHE

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

##---LOCALE-AND-TIME

TIME_ZONE = "Europe/Berlin"
LANGUAGE_CODE = "en-gb"
USE_I18N = True
USE_L10N = True
USE_TZ = True

##---FILES

MEDIA_ROOT = os.path.join(PACKAGE_ROOT, "site_media", "media")
MEDIA_URL = "/site_media/media/"
STATIC_ROOT = os.path.join(PACKAGE_ROOT, "site_media", "static")
STATIC_URL = "/site_media/static/"
SERVE_MEDIA = DEBUG

STATICFILES_DIRS = [
    os.path.join(PACKAGE_ROOT, "static"),
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

FILE_UPLOAD_PERMISSIONS = 0644

ROOT_URLCONF = "host_gnode.urls"
WSGI_APPLICATION = "host_gnode.wsgi.application"
FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

##---TEMPLATES

TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]
TEMPLATE_DIRS = [
    os.path.join(PACKAGE_ROOT, "templates"),
]
TEMPLATE_CONTEXT_PROCESSORS = [
    # common
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    # pinax
    "pinax_utils.context_processors.settings",
    "account.context_processors.account",
    "pinax_theme_bootstrap_account.context_processors.theme",
]

##---MIDDLEWARE

MIDDLEWARE_CLASSES = [
    # common
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # special
    "pagination.middleware.PaginationMiddleware",
    "django_sorting.middleware.SortingMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

##---CORE-APP-LIST

INSTALLED_APPS = [
    # core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # django
    "django.contrib.humanize",
    "django.contrib.webdesign",

    # theme
    "pinax_theme_bootstrap_account",
    "pinax_theme_bootstrap",
    "django_forms_bootstrap",

    # external
    "account",
    "metron",
    "mailer",
    "captcha",
    "pagination",
    "django_sorting",
    "debug_toolbar",
    "south",
]

##---LOGGING

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    }
}

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

##---METRON

METRON_SETTINGS = {
    "google": {
        1: "UA-36729385-1",
    },
}

##---RECAPTCHA

RECAPTCHA_PUBLIC_KEY = "6LfUF9oSAAAAAG7aApg-jWcRIB02lPLBllg1kppz"
RECAPTCHA_PRIVATE_KEY = "6LfUF9oSAAAAAIXDqlPSsmwgzDSB6zkz9Eqs6Czj"
RECAPTCHA_USE_SSL = True

##---DEBUG-TOOLBAR

def dbt_visible(request):
    return request.user.is_authenticated and (DEBUG or request.user.is_superuser or request.user.is_staff)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': dbt_visible,
    'HIDE_DJANGO_SQL': False,
    'ENABLE_STACKTRACES': True,
}

##---IMPORT-LOCAL-SETTINGS

try:
    from .settings_local import *
except Exception, ex:
    print ex

# settings_db

try:
    from .settings_db import *
except Exception, ex:
    print ex

# settings_celery

try:
    from .settings_celery import *
except Exception, ex:
    print ex

##---EOF
