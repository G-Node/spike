##---IMPORTS

from django.core.handlers.wsgi import WSGIHandler
import pinax.env

##---ENVIRONMENT

pinax.env.setup_environ(__file__)

##---WSGI-HANDLER

application = WSGIHandler()

##---MAIN

if __name__ == '__main__':
    pass
