from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns(
    '',
    url(r'^dfiles/', include('dfiles.urls')),
    url(r'^benchmarks/', include('benchmarks.urls')),
    url(r'^evaluations/', include('evaluations.urls')),
    #url(r'^docs/', include('evaldocs.urls')),
    )
