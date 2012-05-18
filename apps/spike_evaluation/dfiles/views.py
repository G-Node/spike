##---IMPORTS

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import get_host, HttpResponse, HttpResponseForbidden
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
import mimetypes
from spike_evaluation.dfiles.models import Datafile
from helpers import render_to

##---VIEWS

@login_required
def upload_progress(request):
    """return JSON object with information about the progress of an upload"""

    if 'HTTP_X_PROGRESS_ID' in request.META:
        progress_id = request.META['HTTP_X_PROGRESS_ID']
        cache_key = '%s_%s' % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)
        json = simplejson.dumps(data)
        return HttpResponse(json)
    else:
        return HttpResponseBadRequest(
            'Server Error: You must provide X-Progress-ID header or query '
            'param.')


@login_required
@render_to('spike_evaluation/dfiles/detail.html')
def detail(request, did):
    """renders a list of versions of a particular file"""

    d = get_object_or_404(Datafile.objects.all(), id=did)
    # security handler
    if not d.is_accessible(request.user):
        d = None
        return HttpResponseForbidden(
            'You don\'t have rights to view or modify.')
    versions = d.version_set.order_by('-version')
    return {'d':d,
            'v_list':versions}


@login_required
def download(request, did, version=None):
    """Processes requests for file download"""

    d = get_object_or_404(Datafile.objects.all(), id=did)
    # security handler
    if not d.is_accessible(request.user):
        d = None
        return HttpResponseForbidden(
            'You don\'t have rights to view or modify.')
    v = d.get_version(version)
    mimetype, encoding = mimetypes.guess_type(v.raw_file.path)
    mimetype = mimetype or 'application/octet-stream'
    response = HttpResponse(v.raw_file.read(), mimetype=mimetype)
    response['Content-Disposition'] = 'attachment; filename=%s' % v.title
    response['Content-Length'] = v.raw_file.size
    if encoding:
        response['Content-Encoding'] = encoding
    response['X-Sendfile'] = str(v.raw_file.path)
    return response

if __name__ == '__main__':
    pass
