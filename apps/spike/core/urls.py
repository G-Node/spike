##---IMPORTS

from django.conf.urls.defaults import *

##---URLS

urlpatterns = patterns('',
    url(r'^algorithm/', include('spike.core.algorithm.urls')),
    url(r'^benchmark/', include('spike.core.benchmark.urls')),
    url(r'^evaluation/', include('spike.core.evaluation.urls')),
)

##---MAIN

if __name__ == '__main__':
    pass
