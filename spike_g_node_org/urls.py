##---IMPORTS

from django.conf import settings
from django.conf.urls.defaults import *
from django.conf.urls.static import static
from django.views.generic import TemplateView
from spike_g_node_org.forms import CaptchaSignupForm

##---ADMIN

from django.contrib import admin

admin.autodiscover()

##---URLS

## core

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='homepage.html'), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/', include("account.urls")),
)

## custom

# TODO: reinstall captcha!!!
urlpatterns += patterns('',
    url(r'^captcha/', include('captcha.urls')),
)

## spike

urlpatterns += patterns('',
    url(r'^', include('spike.urls')),
    url(r'^imprint/$', TemplateView.as_view(template_name='about/imprint.html'), name='imprint'),
    url(r'^team/$', TemplateView.as_view(template_name='about/team.html'), name='team'),
)

## static files

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

##---MAIN

if __name__ == '__main__':
    pass
