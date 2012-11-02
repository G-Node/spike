##---IMPORTS

from django.conf.urls.defaults import patterns, url

##---URLS

urlpatterns = patterns('spike.datafile.views',
    url(r'^download/(?P<pk>\d+)/$',
        'download',
        name='download'),
)

##---MAIN

if __name__ == '__main__':
    pass
