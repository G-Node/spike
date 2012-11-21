# -*- coding: utf-8 -*-
#
# local celery settings - extending the settings.py
#

from settings import *

def default_celery_db_uri():
    rval = "mysql://{USER}".format(**DATABASES['default'])
    if DATABASES['default']['PASSWORD']:
        rval += ":{PASSWORD}".format(**DATABASES['default'])
    if DATABASES['default']['HOST']:
        rval += "@{HOST}".format(**DATABASES['default'])
    else:
        rval += "@localhost"
    if DATABASES['default']['PORT']:
        rval += ":{PORT}".format(**DATABASES['default'])
    rval += "/{NAME}".format(**DATABASES['default'])
    return rval

try:
    import djcelery

    INSTALLED_APPS += ['djcelery']
    BROKER_URL = 'amqp://guest@localhost:5672//'
    CELERY_RESULT_BACKEND = "database"
    CELERY_RESULT_DBURI = default_celery_db_uri()
    USE_CELERY = True

    # DEBUG
    # raise ImportError
    # BUGED

except ImportError:
    USE_CELERY = False
