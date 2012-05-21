from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spike_evaluation.dfiles.views',
    url(r'^upload_progress/$', 'upload_progress', name='d_upload_progress'),
    url(r'^detail/(?P<did>\d+)/$', 'detail', name='d_detail'),
    url(r'^download/(?P<did>\d+)/$', 'download', name='d_download'),
    url(r'^download/(?P<did>\d+)/(?P<version>\d+)/$', 'download',
        name='d_download'),
    )
