from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'system_dashboard.views.state_overview', name="state_overview"),
    url(r'^object_statistics/$', 'system_dashboard.views.object_statistics', name="object_statistics"),
    url(r'^space_usage/$', 'system_dashboard.views.space_usage', name="space_usage"),
)
