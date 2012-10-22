##---IMPORTS

from django.conf.urls.defaults import *

##---URLS

urlpatterns = patterns(
    'spike_eval.benchmark.views',
    url(r'^list/$', 'blist', name='b_list'),
    url(r'^detail/(?P<bid>\d+)/', 'detail', name='b_detail'),
    url(r'^archive/(?P<bid>\d+)/', 'archive', name='b_archive'),
    url(r'^resurrect/(?P<bid>\d+)/', 'resurrect', name='b_resurrect'),
    url(r'^summary/(?P<bid>\d+)/', 'summary', name='b_summary'),
    #url(r'^summary_plot/(?P<bid>\d+)/', 'summary_plot', {'legend': False}, name='b_summary_plot'),
    url(r'^summary_plot/(?P<bid>\d+)/(?P<mode>\w+)/', 'summary_plot', {'legend': False},
        name='b_summary_plot'),
    url(r'^trial/(?P<tid>\d+)/', 'trial', name='b_trial'),
    url(r'^dl_zip/(?P<bid>\d+)/', 'dl_zip', name='b_dl_zip'),
)

##---MAIN

if __name__ == '__main__':
    pass
