##---IMPORTS

from django.conf.urls.defaults import *
from django.views.generic import TemplateView

##---URLS

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='docu/home.html'), name='spike_docu'),
    url(r'^algorithm/', include('spike.algorithm.urls')),
    url(r'^benchmark/', include('spike.benchmark.urls')),
    url(r'^evaluation/', include('spike.evaluation.urls')),
    url(r'^data/', include('spike.data.urls')),
    url(r'^log/', include('spike.log.urls')),
    url(r'^module/', include('spike.module.urls')),
)

##---MAIN

if __name__ == '__main__':
    pass
