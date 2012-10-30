##---IMPORTS

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import models
from django.shortcuts import get_object_or_404
import mimetypes

##---MODEL-REFS

Datafile = models.get_model('spike_eval', 'datafile')

##---VIEWS

@login_required
def datafile(request, did):
    """serve a datafile"""

    d = get_object_or_404(Datafile.objects.all(), id=did)
    mimetype, encoding = mimetypes.guess_type(d.file.path)
    mimetype = mimetype or 'application/octet-stream'
    response = HttpResponse(d.file.read(), mimetype=mimetype)
    response['Content-Disposition'] = 'attachment; filename=%s' % d.name
    response['Content-Length'] = d.file.size
    if encoding:
        response['Content-Encoding'] = encoding
    response['X-Sendfile'] = str(d.file.path)
    return response

if __name__ == '__main__':
    pass
