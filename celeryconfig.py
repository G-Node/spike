# Celery task broker settings
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "portal_user"
BROKER_PASSWORD = "pass"
BROKER_VHOST = "gnodeportal"

# Task Broker Result store settings.
CELERY_RESULT_BACKEND = "database"
CELERY_RESULT_DBURI = "mysql://portal_user:pass@localhost/g-node-dataapi"

