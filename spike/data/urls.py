##---IMPORTS

from django.conf.urls.defaults import patterns, url

##---URLS

urlpatterns = patterns('spike.data.views',
    url(r'^download/(?P<pk>\d+)/$',
        'download',
        name='dt_download'),
    url(r'^delete/(?P<pk>\d+)/$',
        'delete',
        name='dt_delete'),
)

##---MAIN

if __name__ == '__main__':
    pass
