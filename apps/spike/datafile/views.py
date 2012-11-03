##---IMPORTS

import mimetypes
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
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


@login_required
def delete(request, pk):
    """delete datafile"""

    try:
        df = Datafile.objects.get(pk=pk)
        co = df.content_object
        assert co.is_editable(request.user), 'insufficient permissions'
        Datafile.objects.get(pk=pk).delete()
        messages.success(request, 'Datafile "%s" deleted' % df)
    except Exception, ex:
        messages.error(request, 'Datafile not deleted: %s' % ex)
    finally:
        return redirect(co)


if __name__ == '__main__':
    pass
