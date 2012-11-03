##---IMPORTS

from django.conf.urls.defaults import *
from django.views.generic import TemplateView

##---URLS

urlpatterns = patterns('',
    url(r'', include('spike.core.urls')),
    url(r'^metric/', include('spike.metric.urls')),
)

##---MAIN

if __name__ == '__main__':
    pass
