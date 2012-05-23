# -*- coding: utf-8 -*-
#
# general django settings for G-Node project.
# adjusted for spikesorting evaluation website
#
# 2012/05/23 Philipp Meier <pmeier82@googlemail.com>
#

##---IMPORTS

import os
import pinax

##---GENERAL

ABSOLUTE_URL_OVERRIDES = {
    'auth.user':lambda o:'/profiles/profile/%s/' % o.username,
    }

ADMINS = (
    ('Andrey', 'sobolev.andrey@gmail.com'),
    ('Philipp', 'pmeier82@googlemail.com'),
    # ('Your Name', 'your_email@domain.com'),
    )

AUTH_PROFILE_MODULE = 'profiles.Profile'

BEHIND_PROXY = False

DEFAULT_SORT_UP = '&darr;'
DEFAULT_SORT_DOWN = '&uarr;'

FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 # i.e. 1 KB

INTERNAL_IPS = (
    '127.0.0.1',
    )

LANGUAGE_CODE = 'en-gb'
LANGUAGES = (
    ('en', u'English'),
    )

MANAGERS = ADMINS

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

NOTIFICATION_LANGUAGE_MODULE = 'account.Account'

##---CACHE

CACHES = {
    'default':{
        'BACKEND':'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION':'127.0.0.1:11211',
        }
}

##---FILE-UPLOAD

## TODO: check with andrey
#FILE_UPLOAD_HANDLERS = (
#    'datafiles.upload_handlers.UploadProgressCachedHandler',
#    )
#+ global_settings.FILE_UPLOAD_HANDLERS

##--TEMPLATES

TEMPLATE_CONTEXT_PROCESSORS = (
    # default
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    #'django.core.context_processors.static',
    #'django.core.context_processors.tz',
    #'django.contrib.messages.context_processors.messages',

    # extension
    'django.core.context_processors.request',
    'context_processors.pinax_settings',
    'notification.context_processors.notification',
    'announcements.context_processors.site_wide_announcements',
    'account.context_processors.openid',
    'account.context_processors.account',
    'messages.context_processors.inbox',
    'friends_app.context_processors.invitations',
    'context_processors.combined_inbox_count',
    )

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
    os.path.join(PROJECT_ROOT, 'templates', 'default'),
    os.path.join(PROJECT_ROOT, 'site_media', 'static'),
    os.path.join(PINAX_ROOT, 'templates', PINAX_THEME),
    )

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    )

##---MIDDLEWARE

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_openid.consumer.SessionConsumer',
    'account.middleware.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django_sorting.middleware.SortingMiddleware',
    'djangodblog.middleware.DBLogMiddleware',
    'pinax.middleware.security.HideSensistiveFieldsMiddleware',
    'django.middleware.transaction.TransactionMiddleware',

    # 2012/4/16 - pmeier
    'django.contrib.messages.middleware.MessageMiddleware',
    )

##---COMBINED-INBOX

COMBINED_INBOX_COUNT_SOURCES = (
    'messages.context_processors.inbox',
    'friends_app.context_processors.invitations',
    'notification.context_processors.notification',
    )

##---INSTALLED-APPS

INSTALLED_APPS = (
    # django core
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.admin',
    'pinax.templatetags',

    # extension
    'notification', # must be first
    'django_openid',
    'emailconfirmation',
    'friends',
    'messages',
    'announcements',
    'oembed',
    'djangodblog',
    'pagination',
    'gravatar',
    'threadedcomments',
    'threadedcomments_extras',
    'wiki',
    'timezones',
    'tagging',
    'ajax_validation',
    'avatar',
    #'flag',
    #'locations',
    'uni_form',
    'django_sorting',
    #'django_markup',
    'staticfiles',
    'captcha',

    # internal (for now)
    #'projects',
    #'tasks',
    'analytics',
    'profiles',
    'account',
    'signup_codes',
    #'tribes',
    #'photos',
    'tag_app',
    'topics',
    'groups',

    # administration
    'ldap_backend',
    'djcelery',
    'south',

    # spikesorting evaluation
    'spike_evaluation',
    'spike_evaluation.benchmarks',
    'spike_evaluation.dfiles',
    'spike_evaluation.evaluations',
    #'spike_evaluation.evaldocs',

    ## LEGACY: data-api
    #'system_dashboard',
    #'metadata',
    #'timeseries',
    #'neo_api',
    #'state_machine',
    #'trash_folder',
    #'experiments',
    #'datasets',
    #'datafiles',
    ##
    )

##---LOGIN

LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URLNAME = 'home'

##---AVATARS

AVATAR_GRAVATAR_BACKUP = False
AVATAR_DEFAULT_URL = os.path.join(
    STATIC_URL, 'pinax/images/avatar_default.jpeg')

##---MARKUP

MARKUP_FILTER_FALLBACK = 'none'
MARKUP_CHOICES = (
    ('restructuredtext', u'reStructuredText'),
    ('textile', u'Textile'),
    ('markdown', u'Markdown'),
    ('creole', u'Creole'),
    )
FORCE_LOWERCASE_TAGS = True
WIKI_MARKUP_CHOICES = MARKUP_CHOICES
WIKI_REQUIRES_LOGIN = True

class NullStream(object):
    def write(*args, **kwargs):
        pass

    writeline = write
    writelines = write

RESTRUCTUREDTEXT_FILTER_SETTINGS = {
    'cloak_email_addresses':True,
    'file_insertion_enabled':False,
    'raw_enabled':False,
    'warning_stream':NullStream(),
    'strip_comments':True,
    }
