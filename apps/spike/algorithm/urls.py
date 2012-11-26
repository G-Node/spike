##---IMPORTS

from django.conf.urls.defaults import patterns, url

##---URLS

urlpatterns = patterns('spike.algorithm.views',
    url(r'^$',
        'list',
        name='al_list'),
    url(r'^detail/(?P<pk>\d+)/$',
        'detail',
        name='al_detail'),
    url(r'^delete/(?P<pk>\d+)/$',
        'delete',
        name='al_delete'),

)

##---MAIN

if __name__ == '__main__':
    pass
