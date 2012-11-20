##---IMPORTS

from django.conf.urls.defaults import *
from django.views.generic import TemplateView

##---URLS

urlpatterns = patterns('',
    url(r'', include('spike.core.urls')),
    url(r'^data/', include('spike.data.urls')),
    url(r'^log/', include('spike.log.urls')),
    url(r'^metric/', include('spike.metric.urls')),
    url(r'^dev/', include('spike.dev.urls')),
)

##---MAIN

if __name__ == '__main__':
    pass
