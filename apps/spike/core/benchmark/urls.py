##---IMPORTS

from django.conf.urls.defaults import *

##---URLS

urlpatterns = patterns('spike.core.benchmark.views',
    url(r'^$',
        'list',
        name='bm_list'),
    url(r'^detail/(?P<pk>\d+)/$',
        'detail',
        name='bm_detail'),
    url(r'^toggle/(?P<pk>\d+)/$',
        'toggle',
        name='bm_toggle'),
    url(r'^delete/(?P<pk>\d+)/$',
        'delete',
        name='bm_delete'),
    url(r'^summary/(?P<pk>\d+)/$',
        'summary',
        name='bm_summary'),
    url(r'^summary_plot/(?P<pk>\d+)/(?P<mode>\w+)/$',
        'summary_plot',
        {'legend': False},
        name='bm_summary_plot'),
    url(r'^trial/(?P<pk>\d+)/$',
        'trial',
        name='bm_trial'),
    url(r'^zip/(?P<pk>\d+)/$',
        'zip',
        name='bm_zip'),
)

##---MAIN

if __name__ == '__main__':
    pass
