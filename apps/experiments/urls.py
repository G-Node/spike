from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # your experiments
    url(r'^$', 'experiments.views.yourexperiments', name="your_experiments"),
    # all shared experiments (private + public + shared)
    url(r'^allexperiments/$', 'experiments.views.experiments', name='experiments_all'),
    # a members experiments (public + shared)
    url(r'^member_exps/$', 'experiments.views.member_experiments', name='member_experiments'),

    # an experiment details
    url(r'^details/(?P<id>\d+)/$', 'experiments.views.experimentdetails', name="experiment_details"),
    # create new experiment
    url(r'^create/$', 'experiments.views.create', name="experiment_create"),
    #delete experiment
    url(r'^delete/(?P<id>\d+)/$', 'experiments.views.experimentDelete', name='experiment_delete'),
)
