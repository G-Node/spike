##---IMPORTS

from django.conf.urls.defaults import *

##---URLS

urlpatterns = patterns('spike.benchmark.views',
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
    url(r'^summary_plot/(?P<bm_pk>\d+)/(?P<mod_pk>\d+)/(?P<mode>\w+)/$',
        'summary_plot',
        {'legend': False},
        name='bm_summary_plot'),
    url(r'^zip/(?P<pk>\d+)/$',
        'zip',
        name='bm_zip'),
    url(r'^trial/(?P<pk>\d+)/$',
        'trial',
        name='bm_trial'),
    url(r'^trial/delete/(?P<pk>\d+)/$',
        'trial_delete',
        name='bm_trial_delete'),
    url(r'^trial/validate/(?P<pk>\d+)/$',
        'trial_validate',
        name='bm_trial_validate'),
)

##---MAIN

if __name__ == '__main__':
    pass
