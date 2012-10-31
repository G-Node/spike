##---IMPORTS

from django.conf.urls.defaults import *
from views import HomepageView, ImprintView, TeamView

##---URLS

urlpatterns = patterns("",
    url(r'^$', HomepageView.as_view(), name='about'),
    url(r'^imprint/$', ImprintView.as_view(), name='imprint'),
    url(r'^team/$', TeamView.as_view(), name='team'),
    # legacy
    url(r'^terms/$', ImprintView.as_view(), name='terms'),
    url(r'^privacy/$', ImprintView.as_view(), name='privacy'),
)

##---MAIN

if __name__ == '__main__':
    pass
