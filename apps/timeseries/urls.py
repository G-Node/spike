from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # add timeseries
    url(r'^timeseries_add/$', 'timeseries.views.timeseries_add', name="timeseries_add"),
    # remove timeseries
    url(r'^timeseries_delete/$', 'timeseries.views.timeseries_delete', name='timeseries_delete'),
    # edit timeseries
    url(r'^timeseries_edit/$', 'timeseries.views.timeseries_edit', name='timeseries_edit'),
    # all user timeseries
    url(r'^timeseries_main/$', 'timeseries.views.timeseries_main', name="timeseries_main"),
    # timeseries list, depending on section id given
    url(r'^timeseries_list/(?P<id>\d+)/$', 'timeseries.views.timeseries_main', name="timeseries_list"),
)
