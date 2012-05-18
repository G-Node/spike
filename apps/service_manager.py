from django.http import HttpResponseRedirect
from django import forms
from django.core.urlresolvers import reverse

from account.utils import get_default_redirect
#from account.models import other_service, update_other_services
import settings

"""
Service manager allows a user to switch between different G-Node services, for 
example, Data Management or Spike Sorting Evaluation. When user selects a 
different service, visually, the switch happens between GUI contexts; 
technically we change a context varialbe (actual_service), bound to the session,
which defines which context to render (conditioning is done in templates). The 
value of the actual selected service is handled using OtherServiceInfo class.
""" 

def service_selector(request):
    """ Context processor to have actual service in every request."""
    if not request.session.has_key('actual_service'):
        request.session['actual_service'] = settings.DEFAULT_SERVICE
    actual_service = request.session['actual_service']
    return {
        'ACTUAL_SERVICE': actual_service,
        'SUPPORTED_SERVICES': settings.SUPPORTED_SERVICES}


def switch_service(request):
    """ Switch between services. Returns HTTP redirect. """
    url = get_default_redirect(request)
    if request.method == "POST":
        form = SwitchService(request.POST)
        if form.is_valid():
            service_key = form.cleaned_data["service"]
            request.session['actual_service'] = service_key
            if request.user.is_authenticated():
                urlname = settings.LOGIN_REDIRECT_URLNAMES[service_key]
            else:
                urlname = settings.DEFAULT_REDIRECT_URLNAMES[service_key]
            url = reverse(urlname)
    return HttpResponseRedirect(url)


class SwitchService(forms.Form):
    service = forms.ChoiceField(label="Services", required=True, \
        choices=settings.SUPPORTED_SERVICES)
    
