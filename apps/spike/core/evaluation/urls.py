##---IMPORTS

from django.conf.urls.defaults import *

##---URLS

urlpatterns = patterns('spike.core.evaluation.views',
    url(r'^$',
        'list',
        name='ev_list'),
    url(r'^/(?P<pk>\d+)/$',
        'list',
        name='ev_list'),
    url(r'^detail/(?P<pk>\d+)/$',
        'detail',
        name='ev_detail'),
    url(r'^toggle/(?P<pk>\d+)/$',
        'toggle',
        name='ev_toggle'),
    url(r'^delete/(?P<pk>\d+)/$',
        'delete',
        name='ev_delete'),
    url(r'^zip/(?P<pk>\d+)/$',
        'zip',
        name='ev_zip'),
)

##---MAIN

if __name__ == '__main__':
    pass
