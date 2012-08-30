from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spike_eval.evaluation.views',
    # evaluations
    url(r'^list/$', 'elist', name='e_list'),
    url(r'^list/(?P<bid>\d+)/$', 'elist', name='e_list'),
    url(r'^batch/(?P<ebid>\d+)/$', 'batch', name='e_batch'),
    # algorithms
    url(r'^algo_list/$', 'alist', name='a_list'),
    url(r'^algo/(?P<aid>\d+)/$', 'adetail', name='a_detail'),
    )
