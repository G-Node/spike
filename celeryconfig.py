# imports
import djcelery

djcelery.setup_loader()

# celery task broker settings
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "portal"
BROKER_PASSWORD = "pass"
BROKER_VHOST = "localhost"

# celery task broker result storage settings.
CELERY_RESULT_BACKEND = "database"
CELERY_RESULT_DBURI = "mysql://portal:pass@localhost:33306/g-node-spike"

