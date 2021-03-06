# -*- coding: utf-8 -*-
#
# local celery settings - extending the settings.py
#

from .settings import *

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

    djcelery.setup_loader()

    INSTALLED_APPS += ['djcelery']
    BROKER_URL = 'amqp://guest@localhost:5672//'

    CELERY_RESULT_BACKEND = "database"
    CELERY_RESULT_DBURI = default_celery_db_uri()

    #CELERY_RESULT_BACKEND = "amqp"
    #CELERY_TASK_RESULT_EXPIRES = 18000 # 5 hours

    CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

    CELERY_SEND_TASK_ERROR_EMAILS = True
    CELERYD_MAX_TASKS_PER_CHILD = 50 # as long as memleaking is still an issue

    USE_CELERY = True

except ImportError:
    USE_CELERY = False

# override celery usage
CELERY_USE_PRIORITY = False
