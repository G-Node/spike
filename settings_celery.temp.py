# -*- coding: utf-8 -*-
# django-celery settings

try:
    import djcelery

    djcelery.setup_loader()

    BROKER_URL = "amqp://guest@localhost:5672//"
    #CELERY_RESULT_BACKEND = 'amqp'
    CELERY_RESULT_BACKEND = 'database'
    CELERY_RESULT_DBURI = 'mysql://db-user:db-user-pass@localhost/db-name'
except ImportError:
    pass
