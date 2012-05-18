from django.conf import settings
from django.core.urlresolvers import reverse

LOGIN_REDIRECT_URLNAMES = getattr(settings, "LOGIN_REDIRECT_URLNAMES", '')

def get_default_redirect(request, redirect_field_name="next",
        login_redirect_urlnames=LOGIN_REDIRECT_URLNAMES):
    """
    Returns the URL to be used in login procedures by looking at different
    values in the following order:
    
    - LOGIN_REDIRECT_URLNAME - the name of a URLconf entry in the settings
    - LOGIN_REDIRECT_URL - the URL in the setting
    - a REQUEST value, GET or POST, named "next" by default.
    """
    service_key = None
    if request.session.has_key('actual_service'):
        service_key = request.session['actual_service']
    if login_redirect_urlnames and service_key:
        default_redirect_to = reverse(login_redirect_urlnames[service_key])
    else:
        default_redirect_to = settings.LOGIN_REDIRECT_URLNAME
    redirect_to = request.REQUEST.get(redirect_field_name)
    # light security check -- make sure redirect_to isn't garabage.
    if not redirect_to or "://" in redirect_to or " " in redirect_to:
        redirect_to = default_redirect_to
    return redirect_to
