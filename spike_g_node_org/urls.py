##---IMPORTS

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.views.generic import TemplateView
from spike_g_node_org.captcha_signup import CaptchaSignupForm
from account.views import SignupView


##---ADMIN

from django.contrib import admin

admin.autodiscover()

##---URLS

## core

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r"^account/signup/$", SignupView.as_view(form_class=CaptchaSignupForm), name="account_signup"),
    url(r"^account/", include("account.urls")),
)

## custom

#urlpatterns += patterns('',
#    url(r'^captcha/', include('captcha.urls')),
#)

## spike

urlpatterns += patterns('',
    url(r'^spike/', include('spike.urls')),
    url(r'^imprint/$', TemplateView.as_view(template_name='about/imprint.html'), name='imprint'),
    url(r'^team/$', TemplateView.as_view(template_name='about/team.html'), name='team'),
)

## static files

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

##---MAIN

if __name__ == '__main__':
    pass
