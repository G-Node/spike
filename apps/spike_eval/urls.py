##---IMPORTS

from django.conf.urls.defaults import *
from django.views.generic import TemplateView

##---INIT

class HomepageView(TemplateView):
    templatev_name = 'homepage.html'

##---URLS

urlpatterns = patterns('',
    url(r'^$', HomepageView.as_view()),
)

urlpatterns += patterns('spike_eval.views.algorithm',
    url(r'^al_list/$',
        'list',
        name='al_list'),
    url(r'^al_detail/(?P<alid>\d+)/$',
        'detail',
        name='al_detail'),
)

urlpatterns += patterns('spike_eval.views.benchmark',
    url(r'^bm_list/$',
        'list',
        name='bm_list'),
    url(r'^bm_detail/(?P<bmid>\d+)/$',
        'detail',
        name='bm_detail'),
    url(r'^bm_toggle/(?P<bmid>\d+)/$',
        'toggle',
        name='bm_toggle'),
    url(r'^bm_delete/(?P<bmid>\d+)/$',
        'delete',
        name='bm_delete'),
    url(r'^bm_summary/(?P<bmid>\d+)/$',
        'summary',
        name='bm_summary'),
    url(r'^bm_summary_plot/(?P<bmid>\d+)/(?P<mode>\w+)/$',
        'summary_plot',
        {'legend': False},
        name='bm_summary_plot'),
    url(r'^bm_trial/(?P<trid>\d+)/$',
        'trial',
        name='bm_trial'),
    url(r'^bm_zip/(?P<bmid>\d+)/$',
        'zip',
        name='bm_zip'),
)

urlpatterns += patterns('spike_eval.views.datafile',
    url(r'^datafile/(?P<dfid>\d+)/$',
        'datafile',
        name='datafile'),
)

urlpatterns += patterns('spike_eval.views.evaluation',
    url(r'^ev_list/$',
        'list',
        name='ev_list'),
    url(r'^ev_list/(?P<bmid>\d+)/$',
        'list',
        name='ev_list'),
    url(r'^ev_detail/(?P<btid>\d+)/$',
        'detail',
        name='ev_detail'),
    url(r'^ev_toggle/(?P<btid>\d+)/$',
        'toggle',
        name='ev_toggle'),
    url(r'^ev_delete/(?P<btid>\d+)/$',
        'delete',
        name='ev_delete'),
    url(r'^ev_zip/(?P<btid>\d+)/$',
        'zip',
        name='ev_zip'),
)

##---MAIN

if __name__ == '__main__':
    pass
