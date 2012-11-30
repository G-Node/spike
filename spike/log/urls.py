##---IMPORTS

from django.conf.urls import patterns, url

##---URLS

urlpatterns = patterns('spike.log.views',
    url(r'^download/(?P<pk>\d+)/$',
        'download',
        name='lg_download'),
    url(r'^delete/(?P<pk>\d+)/$',
        'delete',
        name='lg_delete'),
)

##---MAIN

if __name__ == '__main__':
    pass
