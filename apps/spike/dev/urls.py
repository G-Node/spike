##---IMPORTS

from django.conf.urls.defaults import *

##---URLS

urlpatterns = patterns('',
    url(r'^signal$', 'signal_test'),
)

##---MAIN

if __name__ == '__main__':
    pass
