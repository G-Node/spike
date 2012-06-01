from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spike_eval.evaluation.views',
    url(r'^list/$', 'list', name='e_list'),
    url(r'^list/(?P<bid>\d+)/$', 'list', name='e_list'),
    url(r'^list/(?P<bid>\d+)/(?P<tid>\d+)/$',
        'list', name='e_list'),
    url(r'^list/(?P<bid>\d+)/(?P<tid>\d+)/(?P<vid>\d+)/$',
        'list', name='e_list'),
    url(r'^detail/(?P<eid>\d+)/$', 'detail', name='e_detail'),
    )
