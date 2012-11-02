##---IMPORTS

from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView

##---URLS

urlpatterns = patterns('spike.core.algorithm.views',
    url(r'^$',
        'list',
        name='al_list'),
    url(r'^detail/(?P<pk>\d+)/$',
        'detail',
        name='al_detail'),
)

##---MAIN

if __name__ == '__main__':
    pass
