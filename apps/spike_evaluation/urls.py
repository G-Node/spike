from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns(
    '',
    url(r'^disclaimer/$', direct_to_template,
            {'template':'spike_evaluation/disclaimer.html'},
        name='spike_disclaimer'),
    url(r'^dfiles/', include('dfiles.urls')),
    url(r'^benchmarks/', include('benchmarks.urls')),
    url(r'^evaluations/', include('evaluations.urls')),
    url(r'^docs/', include('evaldocs.urls')),
    )
