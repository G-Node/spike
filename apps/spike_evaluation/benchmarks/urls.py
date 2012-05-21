from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spike_evaluation.benchmarks.views',
    url(r'^list/$', 'list', name='b_list'),
    url(r'^detail/(?P<bid>\d+)/', 'detail', name='b_detail'),
    url(r'^archive/(?P<bid>\d+)/', 'archive', name='b_archive'),
    url(r'^resurrect/(?P<bid>\d+)/', 'resurrect', name='b_resurrect'),
    url(r'^summary/(?P<bid>\d+)/', 'summary', name='b_summary'),
    url(r'^summary_plot/(?P<bid>\d+)/', 'summary_plot',
        name='b_summary_plot'),
    url(r'^record/(?P<rid>\d+)/', 'record', name='b_record'),
    )
