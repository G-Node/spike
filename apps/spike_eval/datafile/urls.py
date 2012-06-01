##---IMPORTS

from django.conf.urls.defaults import *

##---URLS

urlpatterns = patterns(
    'spike_eval.datafile.views',
    url(r'^download/(?P<did>\d+)/$', 'download', name='d_download'),
    )

##---MAIN

if __name__ == '__main__':
    pass
