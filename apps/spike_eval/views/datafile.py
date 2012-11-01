##---IMPORTS

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.db import models
import mimetypes

##---MODEL-REFS

Datafile = models.get_model('spike_eval', 'datafile')

##---VIEWS

@login_required
def datafile(request, dfid):
    """serve a datafile"""

    # init and checks
    try:
        df = Datafile.objects.get(pk=dfid)
        assert bt.is_accessible(request.user), 'insufficient permissions'
    except Exception, ex:
        messages.error(request, 'You are not allowed to view or modify this Datafile: %s' % ex)
        return Http404()
    mimetype, encoding = mimetypes.guess_type(df.file.path)
    mimetype = mimetype or 'application/octet-stream'
    response = HttpResponse(df.file.read(), mimetype=mimetype)
    response['Content-Disposition'] = 'attachment; filename=%s' % df.name
    response['Content-Length'] = df.file.size
    if encoding:
        response['Content-Encoding'] = encoding
    response['X-Sendfile'] = str(df.file.path)
    return response

if __name__ == '__main__':
    pass
