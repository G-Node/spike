##---IMPORTS

from django.conf.urls.defaults import *
from django.views.generic import TemplateView

##---URLS

urlpatterns = patterns('',
    url(r'^core/', include('spike.core.urls')),
    url(r'^datafile/', include('spike.datafile.urls')),
    url(r'^metric/', include('spike.metric.urls')),
)

##---MAIN

if __name__ == '__main__':
    pass
