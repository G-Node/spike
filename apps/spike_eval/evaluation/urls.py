from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spike_eval.evaluation.views',
    url(r'^list/$', 'elist', name='e_list'),
    url(r'^list/(?P<bid>\d+)/$', 'elist', name='e_list'),
    url(r'^detail/(?P<eid>\d+)/$', 'detail', name='e_detail'),
    url(r'^batch/(?P<ebid>\d+)/$', 'batch', name='e_batch'),
    url(r'^algo_list/$', 'alist', name='a_list'),
    url(r'^algo/(?P<aid>\d+)/$', 'adetail', name='a_detail'),
    )
