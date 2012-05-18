from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    # action selection page
    url(r'^$', direct_to_template, {"template": "datasets/start.html"}, name="start"),
    
    # your datasets
    url(r'^yourdatasets/$', 'datasets.views.yourdatasets', name="your_datasets"),
    # all shared datasets (private + public + shared)
    url(r'^alldatasets/$', 'datasets.views.alldatasets', name='datasets_all'),
    # a members datasets (public + shared)
    #url(r'^member/(?P<username>[\w]+)/$', 'datasets.views.member_datasets', name='member_datasets'),

    # a dataset details
    url(r'^details/(?P<id>\d+)/$', 'datasets.views.datasetdetails', name="dataset_details"),
    # create new dataset
    url(r'^create/$', 'datasets.views.create', name="dataset_create"),
    #delete dataset
    url(r'^delete/(?P<id>\d+)/$', 'datasets.views.datasetDelete', name='dataset_delete'),
    #edit dataset
    url(r'^edit/(?P<id>\d+)/$', 'datasets.views.edit', name='dataset_edit'),
)
