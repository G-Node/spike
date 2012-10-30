##---IMPORTS

from django.conf.urls.defaults import *

##---URLS

urlpatterns = patterns('spike_eval.views.algorithm',
    url(r'^a_list/$',
        'a_list',
        name='a_list'),
    url(r'^a_detail/(?P<aid>\d+)/$',
        'a_detail',
        name='a_detail'),
)

urlpatterns += patterns('spike_eval.views.benchmark',
    url(r'^b_list/$',
        'b_list',
        name='b_list'),
    url(r'^b_detail/(?P<bid>\d+)/',
        'b_detail',
        name='b_detail'),
    url(r'^b_archive/(?P<bid>\d+)/',
        'b_archive',
        name='b_archive'),
    url(r'^b_resurrect/(?P<bid>\d+)/',
        'b_resurrect',
        name='b_resurrect'),
    url(r'^b_summary/(?P<bid>\d+)/',
        'b_summary',
        name='b_summary'),
    url(r'^b_summary_plot/(?P<bid>\d+)/(?P<mode>\w+)/',
        'b_summary_plot',
        {'legend': False},
        name='b_summary_plot'),
    url(r'^b_trial/(?P<tid>\d+)/',
        'b_trial',
        name='b_trial'),
    url(r'^b_zip/(?P<bid>\d+)/',
        'b_zip',
        name='b_zip'),
)

urlpatterns += patterns('spike_eval.views.datafile',
    url(r'^datafile/(?P<did>\d+)/$',
        'datafile',
        name='datafile'),
)

urlpatterns += patterns('spike_eval.views.evaluation',
    # evaluations
    url(r'^e_list/$',
        'e_list',
        name='e_list'),
    url(r'^e_list/(?P<bid>\d+)/$',
        'e_list',
        name='e_list'),
    url(r'^e_batch/(?P<ebid>\d+)/$',
        'e_batch',
        name='e_batch'),
    url(r'^e_zip/(?P<ebid>\d+)/$',
        'e_zip',
        name='e_zip'),
)

##---MAIN

if __name__ == '__main__':
    pass
