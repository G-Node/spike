##---IMPORTS

import mimetypes
from django.http import HttpResponse, Http404
from django.contrib import messages
from .models import Datafile

##---VIEWS

def download(request, pk):
    """serve a datafile for download"""

    try:
        df = Datafile.objects.get(pk=pk)
    except Exception, ex:
        messages.error(request, 'Error downloading Datafile: %s' % ex)
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
