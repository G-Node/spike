##---IMPORTS

from django.conf.urls.defaults import *

##---URLS

urlpatterns = patterns(
    '',
    url(r'^benchmark/', include('spike_eval.benchmark.urls')),
    url(r'^datafile/', include('spike_eval.datafile.urls')),
    url(r'^evaluation/', include('spike_eval.evaluation.urls')),
)

##---MAIN

if __name__ == '__main__':
    pass
