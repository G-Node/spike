##---IMPORTS

from django.conf import settings
from django.conf.urls.defaults import *
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from pinax.apps.account.openid_consumer import PinaxConsumer
from pinax.apps.account.urls import signup_view
from staticfiles.urls import staticfiles_urlpatterns
from forms import CaptchaSignupForm

##---INIT

admin.autodiscover()
handler500 = 'pinax.views.server_error'

class HomepageView(TemplateView):
    template_name = 'homepage.html'

##---URLS

urlpatterns = patterns('',
    url(r'^$', HomepageView.as_view(), name='home'),
    url(r'^admin/invite_user/$', 'pinax.apps.signup_codes.views.admin_invite_user', name='admin_invite_user'),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    # pinax base urls
    url(r'^about/', include('about.urls')),
    url(r'^account/', include('pinax.apps.account.urls')),
    url(r'^openid/', include(PinaxConsumer().urls)),
    url(r'^profiles/', include('idios.urls')),
    url(r'^notices/', include('notification.urls')),
    url(r'^announcements/', include('announcements.urls')),
)

urlpatterns += patterns('',
    url(r'^captcha/', include('captcha.urls')),
    url(r'^signup/$', signup_view, {'form_class': CaptchaSignupForm}, name='acct_signup'),
)

urlpatterns += patterns('',
    url(r'^spike_eval/', include('spike_eval.urls')),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

##---MAIN

if __name__ == '__main__':
    pass
