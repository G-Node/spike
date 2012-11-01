##---IMPORTS

from django.conf.urls.defaults import *
from apps.spike_dev.views import AlgorithmListView
from django.views.generic import TemplateView

##---CLASSES

class HomepageView(TemplateView):
    template_name = 'homepage.html'

##---URLS

urlpatterns = patterns('')

urlpatterns += patterns('spike_dev.views',
    url(r'^a_list/$',
        AlgorithmListView.as_view()),
    url(r'^display_meta/$',
        'display_meta'),
    url(r'^home/$', HomepageView.as_view()),
)

##---MAIN

if __name__ == '__main__':
    pass
