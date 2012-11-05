##---IMPORTS

import mimetypes
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import LogItem

##---VIEWS

def download(request, pk):
    """serve a datafile for download"""

    try:
        lg = LogItem.objects.get(pk=pk)
    except Exception, ex:
        messages.error(request, 'Error downloading LogItem: %s' % ex)
        return Http404()
    response = HttpResponse(mimetype='text/plain')
    response.write(lg.text)
    return response


@login_required
def delete(request, pk):
    """delete datafile"""

    try:
        lg = LogItem.objects.get(pk=pk)
        co = lg.content_object
        # TODO: permissions?
        LogItem.objects.get(pk=pk).delete()
        messages.success(request, 'Logitem "%s" deleted' % lg)
    except Exception, ex:
        messages.error(request, 'LogItem not deleted: %s' % ex)
    finally:
        return redirect(co)


if __name__ == '__main__':
    pass
