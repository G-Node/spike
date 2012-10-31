##---IMPORTS

from django.conf.urls.defaults import *
from views import AlgorithmListView

##---URLS

urlpatterns = patterns('')

urlpatterns += patterns('spike_eval.dev.views',
    url(r'^a_list/$',
        AlgorithmListView.as_view()),
    url(r'^display_meta/$',
        'display_meta'),
)

##---MAIN

if __name__ == '__main__':
    pass
