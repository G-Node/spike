from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    # here supported -> GET: query all category, PUT/POST: create new
    url(r'^(?P<obj_type>[\w]+)/?$', 'neo_api.views.handle_category', \
        name="handle_category"),

    # here supported -> GET: get single object, PUT/POST: update, DELETE: delete
    # serve partial data requests (info, data etc.) using GET params
    url(r'^(?P<obj_type>[\w]+)/(?P<obj_id>[\d]+)/?$', \
        'neo_api.views.handle_object', name="handle_object"),

    # deprecated
    #url(r'^$', 'neo_api.views.process', name="create"), # do smth at root?
    #url(r'^delete/(?P<neo_id>[\w]+_[\d]+)/$', 'neo_api.views.delete', name="delete"),
    #url(r'^(?P<enquery>[\w]+)/(?P<neo_id>[\w]+_[\d]+)/$', 'neo_api.views.retrieve', name="retrieve"),
    #url(r'^(?P<neo_id>[\w]+_[\d]+)/$', 'neo_api.views.process', name="process"),
    #url(r'^(?P<neo_id>[\w]+_[\d]+)$', 'neo_api.views.process', name="process"),
    # - that's a jerky workaround for POST without trailing slash. If there are
    # more POST requests, better change to middleware:
    # http://djangosnippets.org/snippets/601/
    # linking with values goes to values update API
    #url(r'^assign/(?P<neo_id>[\w]+_[\d]+)/$', 'neo_api.views.assign', name="assign"),
    #url(r'^select/(?P<obj_type>[\w]+)/$', 'neo_api.views.select', name="select"),
)
