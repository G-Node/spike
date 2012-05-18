from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^section_add/$', 'metadata.views.section_add', name="section_add"),
    url(r'^section_delete/$', 'metadata.views.section_delete', name='section_delete'),
    url(r'^section_edit/$', 'metadata.views.section_edit', name='section_edit'),
    url(r'^section_move/$', 'metadata.views.section_move', name='section_move'),
    url(r'^section_copy/$', 'metadata.views.section_copy', name='section_copy'),

    url(r'^properties_list/(?P<id>\d+)/$', 'metadata.views.properties_list', name="properties_list"),
    url(r'^property_add/(?P<id>\d+)/$', 'metadata.views.property_add', name="property_add"),
    url(r'^property_edit/(?P<id>\d+)/$', 'metadata.views.property_edit', name='property_edit'),
    url(r'^dataset_link/(?P<id>\d+)/$', 'metadata.views.object_link', name="dataset_link"),
    url(r'^datafile_link/(?P<id>\d+)/$', 'metadata.views.object_link', name="datafile_link"),
    url(r'^timeseries_link/(?P<id>\d+)/$', 'metadata.views.object_link', name="timeseries_link"),

    url(r'^import_odml/(?P<id>\d+)/$', 'metadata.views.import_odml', name="import_odml"),
    url(r'^export_odml/(?P<id>\d+)/$', 'metadata.views.export_odml', name="export_odml"),

    url(r'^property_delete/$', 'metadata.views.property_delete', name='property_delete'),
    url(r'^remove_dataset/$', 'metadata.views.remove_object', name='remove_dataset'),
    url(r'^remove_datafile/$', 'metadata.views.remove_object', name='remove_datafile'),
    url(r'^remove_timeseries/$', 'metadata.views.remove_object', name='remove_timeseries'),

)
