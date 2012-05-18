from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, get_host, HttpResponse, HttpResponseForbidden
from django.template import RequestContext
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

import logging
import mimetypes
import os.path

from datafiles.models import Datafile
from datasets.models import RDataset
from experiments.models import Experiment
from metadata.models import Section
from datafiles.tasks import extract_file_info, extract_from_archive # broker tasks

from datafiles.forms import NewDatafileForm, DatafileEditForm, DeleteDatafileForm, DatafileShortEditForm, PrivacyEditForm
from metadata.forms import AddPropertyForm, LinkTSForm, importOdML

#LOG_FILENAME = '/data/apps/g-node-portal/g-node-portal/logs/test_upload.txt'
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

def upload_progress(request):
    """
    Return JSON object with information about the progress of an upload.
    """
    if 'HTTP_X_PROGRESS_ID' in request.META:
        progress_id = request.META['HTTP_X_PROGRESS_ID']
        from django.utils import simplejson
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)
        #logging.debug('%s - cache key', cache_key)
        json = simplejson.dumps(data)
        return HttpResponse(json)
    else:
        #logging.error("Received progress report request without X-Progress-ID header. request.META: %s" % request.META)
        return HttpResponseBadRequest('Server Error: You must provide X-Progress-ID header or query param.')


@login_required
def create(request, form_class=NewDatafileForm, template_name="datafiles/new.html"):
    """
    create a new datafile
    """
    datafile_form = form_class(request.user)
    if request.method == 'POST':
        if request.POST.get("action_1") == "upload":
            #logging.debug('start uploading the file')
            datafile_form = form_class(request.user, request.POST, request.FILES)
            if datafile_form.is_valid():
                datafile = datafile_form.save(commit=False)
                datafile.owner = request.user
                datafile.title = request.FILES['raw_file'].name
                datafile.save()
                datafile_form.save_m2m()
                # start a task to extract neuroshare info TODO return extracted
                extracted = extract_file_info.delay(datafile.id)
                task_id = str(extracted.task_id) # this line is required, due to short tasks
                datafile.last_task_id = task_id
                datafile.save()
                request.user.message_set.create(message=_("Successfully created datafile '%s'") % datafile.title)
                include_kwargs = {"id": datafile.id}
		redirect_to = reverse("your_datafiles")
		return HttpResponseRedirect(redirect_to)
                
    return render_to_response(template_name, {
        "datafile_form": datafile_form,
    }, context_instance=RequestContext(request))


@login_required
def yourdatafiles(request, template_name="datafiles/your_datafiles.html"):
    """
    datafiles owned by the currently authenticated user
    """
    
    datafiles = Datafile.objects.filter(owner=request.user, current_state=10)
    datafiles = datafiles.order_by("-date_added")
    set_objects_form = DeleteDatafileForm(request.POST or None, user=request.user)
    
    action = request.POST.get("action")
    if request.method == 'POST' and action == "delete":
        if set_objects_form.is_valid():
            ids = set_objects_form.cleaned_data['set_choices']
            for datafile in Datafile.objects.filter(id__in=ids):
                if datafile.owner == request.user:
                    datafile.deleteObject()
                    datafile.save()
            request.user.message_set.create(message=_("Successfully deleted the requested datafiles."))
            redirect_to = reverse("your_datafiles")
            return HttpResponseRedirect(redirect_to)

    return render_to_response(template_name, {
        "datafiles": datafiles,
    }, context_instance=RequestContext(request))


@login_required
def alldatafiles(request, template_name="datafiles/all.html"):
    """
    all datafiles available for you
    """

    datafiles = Datafile.objects.filter(Q(current_state=10))
    datafiles = datafiles.exclude(owner=request.user, safety_level=3).exclude(owner=request.user, safety_level=2)
    
    search_terms = request.GET.get('search', '')
    if search_terms:
        datafiles = (datafiles.filter(title__icontains=search_terms) |
            datafiles.filter(caption__icontains=search_terms))
    datafiles = datafiles.order_by("-date_added")
    datafiles = filter(lambda x: x.is_accessible(request.user), datafiles)
    
    return render_to_response(template_name, {
        "datafiles": datafiles,
        "search_terms": search_terms,	
    }, context_instance=RequestContext(request))


@login_required
def datafiledetails(request, id, form_class=DatafileShortEditForm, privacy_form_class=PrivacyEditForm, 
    timeseries_form_class=LinkTSForm, property_form_class1=AddPropertyForm, template_name="datafiles/details.html"):
    """
    show the datafile details
    """

    datafiles = Datafile.objects.all()
    datafile = get_object_or_404(datafiles, id=id)
    datafiles = None
    
    # security handler
    if not datafile.is_accessible(request.user):
        return HttpResponseForbidden("This action is forbidden")

    action = request.POST.get("action")

    # edit details handler
    if request.user == datafile.owner and action == "details_update":
        datafile_form = form_class(request.POST, instance=datafile)
        if datafile_form.is_valid():
            datafile = datafile_form.save()
    else:
        datafile_form = form_class(instance=datafile)
    
    # edit privacy handler    
    if request.user == datafile.owner and action == "privacy_update":
        privacy_form = privacy_form_class(request.user, request.POST, instance=datafile)
        if privacy_form.is_valid():
            datafile = privacy_form.save()
    else:
        privacy_form = privacy_form_class(user=request.user, instance=datafile)

    # templates for metadata. can't move to state_mashine due to import error
    metadata_defaults = []
    for section in Section.objects.filter(current_state=10, is_template=True):
        if not section.parent_section:
            metadata_defaults.append(section.get_tree())
    for section in Section.objects.filter(current_state=10, user_custom=datafile.owner):
        if not section.parent_section:
            metadata_defaults.append(section.get_tree())

    prop_add_form = property_form_class1(auto_id='id_add_form_%s')
    timeseries_link_form = timeseries_form_class(auto_id='id_timeseries_form_%s', user=request.user)
    odml_import_form = importOdML(auto_id='id_odml_form_%s', user=request.user)

    # get the parent objects to which this file is linked to
    par_datasets = []
    par_exprts = []
    sections = Section.objects.filter(current_state=10)
    sections = filter(lambda x: x.has_datafile(datafile.id), sections)
    for section in sections:
        rt = section.get_root()
        if rt and (not rt in par_datasets) and (not rt in par_exprts):
            if isinstance(rt, RDataset):
                par_datasets.append(rt)
            elif isinstance(rt, Experiment):
                par_exprts.append(rt)

    # get the id of the first available section to select it in the tree (onload)
    first_section_id = request.GET.get("section_id")
    if not first_section_id:
        sections = datafile.section_set.filter(current_state=10).order_by("tree_position")
        if sections:
            first_section_id = sections[0].id

    return render_to_response(template_name, {
        "datafile": datafile,
        "metadata_defaults": metadata_defaults,
        "datafile_form": datafile_form,
        "privacy_form": privacy_form,	
        "prop_add_form": prop_add_form,
        "timeseries_link_form": timeseries_link_form,
        "odml_import_form": odml_import_form,
        "par_datasets": par_datasets,
        "par_exprts": par_exprts,
        "first_section_id": first_section_id,
    }, context_instance=RequestContext(request))


@login_required
def datafileDelete(request, id):
    """
    Deletes a datafile by id provided.
    """
    datafiles = Datafile.objects.all()
    datafile = get_object_or_404(datafiles, id=id)
    title = datafile.title
    redirect_to = reverse("your_datafiles")
    if not datafile.owner == request.user:
        return HttpResponseForbidden("This action is forbidden")
    datafile.deleteObject()
    datafile.save()
    request.user.message_set.create(message=_("Successfully deleted datafile '%s'") % title)
    return HttpResponseRedirect(redirect_to)


@login_required
def download(request, id):
    """
    Processes requests for file download.
    An alternative way is to use xsendfile:
    #response = HttpResponse(mimetype='application/force-download')
    #response['Content-Disposition'] = 'attachment; filename=%s' % (datafile.title)
    """
    datafile = get_object_or_404(Datafile.objects.all(), id=id)
    # security handler
    if not datafile.is_accessible(request.user):
        datafile = None
        raise Http404
    mimetype, encoding = mimetypes.guess_type(datafile.raw_file.path)
    mimetype = mimetype or 'application/octet-stream' 
    response = HttpResponse(datafile.raw_file.read(), mimetype=mimetype)
    response['Content-Disposition'] = 'attachment'
    response['Content-Length'] = datafile.raw_file.size 
    if encoding: 
        response["Content-Encoding"] = encoding
    return response


@login_required
def extract(request, id):
    """ Extract files/folders from the file if archive."""
    datafile = get_object_or_404(Datafile.objects.all(), id=id)
    # security handler
    if not datafile.owner == request.user:
        datafile = None
        return HttpResponseForbidden()
    if datafile.is_archive: # start a task to extract from archive
        extracted = extract_from_archive.delay(datafile.id)
        task_id = str(extracted.task_id) # this line is required, due to short tasks
        datafile.last_task_id = task_id
        datafile.extracted = "processing"
        datafile.save()
    return HttpResponse("The extraction task has been started.")
    
