##---IMPORTS

from django.conf.urls.defaults import patterns, url

##---URLS

urlpatterns = patterns('spike.core.datafile.views',
    url(r'^download/(?P<pk>\d+)/$',
        'download',
        name='df_download'),
    url(r'^delete/(?P<pk>\d+)/$',
        'delete',
        name='df_delete'),

)

##---MAIN

if __name__ == '__main__':
    pass
