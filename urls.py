##---IMPORTS

from django.conf import settings
from django.conf.urls.defaults import *
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from pinax.apps.account.openid_consumer import PinaxConsumer
from pinax.apps.account.urls import signup_view
from staticfiles.urls import staticfiles_urlpatterns
from forms import CaptchaSignupForm

##---INITS

admin.autodiscover()
handler500 = 'pinax.views.server_error'

##---URLS

urlpatterns = patterns("",

    # static pages and admin
    url(r'^$', direct_to_template, {'template': 'homepage.html'}, name='home'),
    url(r'^team$', direct_to_template, {'template': 'team.html'}, name='team'),
    url(r'^imprint$', direct_to_template, {'template': 'imprint.html'}, name='imprint'),
    url(r'^admin/invite_user/$',
        'pinax.apps.signup_codes.views.admin_invite_user',
        name='admin_invite_user'),
    url(r'^admin/', include(admin.site.urls)),

    # pinax base urls
    url(r'^about/', include('about.urls')),
    url(r'^account/', include('pinax.apps.account.urls')),
    url(r'^openid/', include(PinaxConsumer().urls)),
    url(r'^profiles/', include('idios.urls')),
    url(r'^notices/', include('notification.urls')),
    url(r'^announcements/', include('announcements.urls')),

    # captcha
    url(r'^captcha/', include('captcha.urls')),
    url(r"^account/signup/$", signup_view, {'form_class': CaptchaSignupForm}, name="acct_signup"),

    # spike-eval
    url(r'^spike_eval/', include('spike_eval.urls')),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

##---MAIN

if __name__ == '__main__':
    pass
