
from django.shortcuts import render_to_response, get_object_or_404
#from django.core.exceptions import ObjectDoesNotExist
#from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_app
from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.translation import ugettext
from experiments.models import Experiment
from datasets.models import RDataset
from datafiles.models import Datafile
from trash_folder.forms import RestoreExperimentsForm
from trash_folder.forms import RestoreDatasetsForm
from trash_folder.forms import RestoreFilesForm
from django.utils.translation import ugettext as _

try:
    notification = get_app('notification')
except ImproperlyConfigured:
    notification = None

def trashContents_Exps(request, template_name="trash_folder/exp_contents.html"):
    
    exp_objects = Experiment.objects.filter(Q(current_state=20, owner=request.user)).order_by('-date_created')
    exp_objects_form = RestoreExperimentsForm(request.POST or None, user=request.user)

    if request.method == 'POST':
        if exp_objects_form.is_valid():
            ids = exp_objects_form.cleaned_data['exp_choices']
            for exp in Experiment.objects.filter(id__in=ids):
	    	exp.restoreObject()
		exp.save()
            request.user.message_set.create(message=_("Successfully restored the requested objects."))
            redirect_to = reverse("deletedExperiments")
            return HttpResponseRedirect(redirect_to)
	    
    return render_to_response(template_name, {
        #"exp_objects_form": exp_objects_form,
        "exp_objects": exp_objects,
    }, context_instance=RequestContext(request))

def trashContents_Datasets(request, template_name="trash_folder/set_contents.html"):
    
    set_objects = RDataset.objects.filter(Q(current_state=20, owner=request.user)).order_by('-date_added')
    set_objects_form = RestoreDatasetsForm(request.POST or None, user=request.user)

    if request.method == 'POST':
        if set_objects_form.is_valid():
            ids = set_objects_form.cleaned_data['set_choices']
            for rdataset in RDataset.objects.filter(id__in=ids):
	    	rdataset.restoreObject()
		rdataset.save()
            request.user.message_set.create(message=_("Successfully restored the requested objects."))
            redirect_to = reverse("deletedDatasets")
            return HttpResponseRedirect(redirect_to)
	    
    return render_to_response(template_name, {
        #"set_objects_form": set_objects_form,
        "set_objects": set_objects,
    }, context_instance=RequestContext(request))

def trashContents_Files(request, template_name="trash_folder/file_contents.html"):
    
    fil_objects = Datafile.objects.filter(Q(current_state=20, owner=request.user)).order_by('-date_added')
    fil_objects_form = RestoreFilesForm(request.POST or None, user=request.user)

    if request.method == 'POST':
        if fil_objects_form.is_valid():
            ids = fil_objects_form.cleaned_data['fil_choices']
            for datafile in Datafile.objects.filter(id__in=ids):
	    	datafile.restoreObject()
		datafile.save()
            request.user.message_set.create(message=_("Successfully restored the requested objects."))
            redirect_to = reverse("deletedFiles")
            return HttpResponseRedirect(redirect_to)
	    
    return render_to_response(template_name, {
        #"fil_objects_form": fil_objects_form,
        "fil_objects": fil_objects,
    }, context_instance=RequestContext(request))