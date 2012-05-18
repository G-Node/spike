from django.conf.urls.defaults import * 
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    # your datafiles
    url(r'^$', 'datafiles.views.yourdatafiles', name="your_datafiles"),
    # all shared datafiles (private + public + shared)
    url(r'^alldatafiles/$', 'datafiles.views.alldatafiles', name='datafiles_all'),
    # a members datafiles (public + shared)
    #url(r'^member/(?P<username>[\w]+)/$', 'datafiles.views.member_datafiles', name='member_datafiles'),

    # a datafile details
    url(r'^details/(?P<id>\d+)/$', 'datafiles.views.datafiledetails', name="datafile_details"),
    # create new datafile
    url(r'^create/$', 'datafiles.views.create', name="datafile_create"),
    #delete datafile
    url(r'^delete/(?P<id>\d+)/$', 'datafiles.views.datafileDelete', name='datafile_delete'),

    # create single datafile
    url(r'^create/$', 'datafiles.views.create', name="datafile_create"),
    # file upload status for progress bar 
    
    # test upload
    #url(r'^test_upload/$', 'datafiles.views.test_upload', name='test_upload'),
    url(r'^upload_progress/$', 'datafiles.views.upload_progress', name='upload_progress'),

    # datafile download link
    url(r'^download/(?P<id>\d+)/', 'datafiles.views.download', name="download"),

    url(r'^extract/(?P<id>\d+)/', 'datafiles.views.extract', name="extract"),

    # GWT multiple datafiles upload
    #url(r'^create_multiple/$', 'datafiles.views.create_multiple', name="datafile_create_multiple"),
    #url(r'^upload_page/$', 'datafiles.views.upload_page', name='upload_page'),
    #url(r'^upload_file/$', 'datafiles.views.upload_file', name='upload_file'),
)
