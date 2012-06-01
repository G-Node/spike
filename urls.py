##---IMPORTS

from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.conf.urls.static import static

from django.contrib import admin

admin.autodiscover()

from staticfiles.urls import staticfiles_urlpatterns

from pinax.apps.account.openid_consumer import PinaxConsumer

handler500 = 'pinax.views.server_error'

##---URLS

urlpatterns = patterns(
    "",

    # sandbox

    # landing page and admin
    url(r'^$', direct_to_template, {
        'template':'homepage.html',
        }, name='home'),
    url(r"^admin/invite_user/$",
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

    # spike-eval
    url(r'^spike_eval/', include('spike_eval.urls')),
    )

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

##---MAIN

if __name__ == '__main__':
    pass
