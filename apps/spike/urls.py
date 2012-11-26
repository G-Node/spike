##---IMPORTS

from django.conf.urls.defaults import *
from django.views.generic import TemplateView

##---URLS

urlpatterns = patterns('',
    url(r'^algorithm/', include('spike.algorithm.urls')),
    url(r'^benchmark/', include('spike.benchmark.urls')),
    url(r'^evaluation/', include('spike.evaluation.urls')),
    url(r'^data/', include('spike.data.urls')),
    url(r'^log/', include('spike.log.urls')),
    url(r'^module/', include('spike.module.urls')),
    url(r'^dev/', include('spike.dev.urls')),
)

##---MAIN

if __name__ == '__main__':
    pass
