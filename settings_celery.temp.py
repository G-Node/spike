# -*- coding: utf-8 -*-
#
# local celery settings - extending the settings.py
#

from settings import *

try:
    import djcelery

    djcelery.setup_loader()

    INSTALLED_APPS += ["djcelery"]
    USE_CELERY = True
    BROKER_URL = "amqp://guest@localhost:5672//"
    #CELERY_RESULT_BACKEND = "amqp"
    CELERY_RESULT_BACKEND = "database"
    CELERY_RESULT_DBURI = "mysql://db-user:db-user-pass@localhost/db-name"
except ImportError:
    pass
