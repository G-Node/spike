"""
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {"template": "about/about.html"}, name="about"),
    )
"""
