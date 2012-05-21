# imports
import djcelery

djcelery.setup_loader()

# celery task broker settings
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "portal_user"
BROKER_PASSWORD = "pass"
BROKER_VHOST = "gnodeportal"

# celery task broker result storage settings.
CELERY_RESULT_BACKEND = "database"
CELERY_RESULT_DBURI = "mysql://portal_user:pass@localhost/g-node-spike"

