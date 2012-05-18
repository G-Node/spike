from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, get_host
from django.template import RequestContext
from django.db.models import Q
from django.http import Http404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime
from datetime import timedelta

from experiments.models import Experiment
from datasets.models import RDataset
from datafiles.models import Datafile
from experiments.forms import CreateExperimentForm, ExperimentShortEditForm, PrivacyEditForm, DeleteExperimentsForm
from experiments.filters import ExpFilter
from metadata.forms import AddPropertyForm, LinkDatasetForm, LinkDatafileForm, LinkTSForm, importOdML
from metadata.models import Section

@login_required
def create(request, form_class=CreateExperimentForm,
        template_name="experiments/create.html"):
    """
    form to create experiments
    """
    
    exp_form = form_class(request.user)
    if request.method == 'POST':
        if request.POST.get("action") == "create":
            exp_form = form_class(request.user, request.POST)
            if exp_form.is_valid():
                experiment = exp_form.save(commit=False)
                experiment.owner = request.user
                experiment.save()
                exp_form.save_m2m()
                request.user.message_set.create(message=_("Successfully created experiment '%s'") % experiment.title)
                include_kwargs = {"id": experiment.id}
                redirect_to = reverse("experiment_details", kwargs=include_kwargs)
                
                return HttpResponseRedirect(redirect_to)

    return render_to_response(template_name, {
        "exp_form": exp_form,
    }, context_instance=RequestContext(request))


@login_required
def yourexperiments(request, template_name="experiments/yourexperiments.html"):
    """
    experiments for the currently authenticated user
    """
    set_objects_form = DeleteExperimentsForm(request.POST or None, user=request.user)
    action = request.POST.get("action")
    if request.method == 'POST' and action == "delete":
        if set_objects_form.is_valid():
            ids = set_objects_form.cleaned_data['set_choices'] # [u'39', u'20', u'18']
            for exprt in Experiment.objects.filter(id__in=ids):
                if exprt.owner == request.user:
                    exprt.deleteObject()
                    exprt.save()
                else:
                    raise Http404
            request.user.message_set.create(message=("Successfully deleted requested experiments. All related objects are still available"))
    
    experiments = Experiment.objects.filter(owner=request.user, current_state=10)
    experiments = experiments.order_by("-date_created")

    today = datetime.date.today()
    prev_month = today.month - 1
    prev_year = today.year
    if prev_month == 0:
        prev_month = 12
        prev_year = prev_year - 1
    f_1 = 'all'
    f_2 = 'last week'
    f_3 = 'last month'
    f_4 = str(today.strftime("%B %Y"))
    f_5 = str(datetime.date(prev_year, prev_month, 1).strftime("%B %Y"))

    if request.POST.get("fltr"):
        fltr = request.POST.get("fltr")
    else:
        fltr = "all"
    
    if 'filter_choice' in request.POST:
        fltr = request.POST.get("filter_choice")
	if fltr == 'last week':
	    days = timedelta(days=6)
	    experiments = experiments.filter(date_created__range=(today - days, today))
	elif fltr == 'last month':
	    days = timedelta(days=31)
	    experiments = experiments.filter(date_created__range=(today - days, today))
	elif fltr == str(today.strftime("%B %Y")):
	    experiments = experiments.filter(date_created__month=today.month)
	elif fltr == str(datetime.date(prev_year, prev_month, 1).strftime("%B %Y")):
	    experiments = experiments.filter(date_created__month=prev_month, date_created__year=prev_year)
	    
    return render_to_response(template_name, {
        "experiments": experiments,
        "fltr": fltr,
        "f_1": f_1,
        "f_2": f_2,
        "f_3": f_3,
        "f_4": f_4,
        "f_5": f_5,
    }, context_instance=RequestContext(request))

@login_required
def experiments(request, template_name="experiments/all.html"):
    # all experiments available for the user
    experiments = Experiment.objects.filter(Q(current_state=10))
    experiments = experiments.exclude(owner=request.user, safety_level=3).exclude(owner=request.user, safety_level=2)
    
    search_terms = request.GET.get('search', '')
    if search_terms:
        experiments = (experiments.filter(title__icontains=search_terms) |
            experiments.filter(caption__icontains=search_terms))
    experiments = experiments.order_by("-date_created")
    experiments = filter(lambda x: x.is_accessible(request.user), experiments)
    
    #content_type = ContentType.objects.get_for_model(Project)
    #projects = projects.extra(select=SortedDict([
    #    ('member_count', MEMBER_COUNT_SQL),
    #    ('topic_count', TOPIC_COUNT_SQL),
    #]), select_params=(content_type.id,))
    
    return render_to_response(template_name, {
        "experiments": experiments,
        "search_terms": search_terms,
    }, context_instance=RequestContext(request))


@login_required
def member_experiments(request, template_name="experiments/memberexperiments.html"):
    # method temporary not used..

    experiments = Experiment.objects.filter(Q(safety_level=1), Q(current_state=10), ~Q(owner=request.user))
    #experiments = filter(lambda x: x != request.user.id, experiments)
    experiments = experiments.order_by("owner")
    
    return render_to_response(template_name, {
        "experiments": experiments,
    }, context_instance=RequestContext(request))


@login_required
def experimentdetails(request, id, form_class=ExperimentShortEditForm, privacy_form_class=PrivacyEditForm, 
	dataset_form_class=LinkDatasetForm, datafile_form_class=LinkDatafileForm,
    timeseries_form_class=LinkTSForm, property_form_class1=AddPropertyForm, template_name="experiments/details.html"):
    # show the experiment details
    experiment = get_object_or_404(Experiment.objects.all(), id=id)

    # security handler
    if not experiment.is_accessible(request.user):
        experiment = None
        raise Http404

    action = request.POST.get("action")
    if request.user == experiment.owner:
	    # edit details handler
	    if action == "details_update":
		exp_form = form_class(request.POST, instance=experiment)
		if exp_form.is_valid():
		    experiment = exp_form.save()
	            request.user.message_set.create(message=_("Successfully updated experiment '%s'") % experiment.title)
	    else:
		exp_form = form_class(instance=experiment)

	    # edit privacy handler    
	    if action == "privacy_update":
		privacy_form = privacy_form_class(request.user, request.POST, instance=experiment)
		if privacy_form.is_valid():
		    experiment = privacy_form.save()
		    request.user.message_set.create(message=_("New privacy settings for '%s' saved") % experiment.title)
	    else:
		privacy_form = privacy_form_class(user=request.user, instance=experiment)
    else:
        exp_form = form_class(instance=experiment)
        privacy_form = privacy_form_class(user=request.user, instance=experiment)

    # templates for metadata. can't move to state_mashine due to import error
    metadata_defaults = []
    for section in Section.objects.filter(current_state=10, is_template=True):
        if not section.parent_section:
            metadata_defaults.append(section.get_tree())
    for section in Section.objects.filter(current_state=10, user_custom=experiment.owner):
        if not section.parent_section:
            metadata_defaults.append(section.get_tree())

    prop_add_form = property_form_class1(auto_id='id_add_form_%s')
    dataset_link_form = dataset_form_class(auto_id='id_dataset_form_%s', user=request.user)
    datafile_link_form = datafile_form_class(auto_id='id_datafile_form_%s', user=request.user)
    timeseries_link_form = timeseries_form_class(auto_id='id_timeseries_form_%s', user=request.user)
    odml_import_form = importOdML(auto_id='id_odml_form_%s', user=request.user)

    # get the id of the first available section to select it in the tree (onload)
    first_section_id = request.GET.get("section_id")
    if not first_section_id:
        sections = experiment.section_set.filter(current_state=10).order_by("tree_position")
        if sections:
            first_section_id = sections[0].id

    return render_to_response(template_name, {
        "experiment": experiment,
        "metadata_defaults": metadata_defaults,
	    "exp_form": exp_form,
	    "privacy_form": privacy_form,
        "prop_add_form": prop_add_form,
        "dataset_link_form": dataset_link_form,
        "datafile_link_form": datafile_link_form,
        "timeseries_link_form": timeseries_link_form,
        "odml_import_form": odml_import_form,
        "first_section_id": first_section_id,
    }, context_instance=RequestContext(request))


@login_required
def experimentDelete(request, id):
  
    experiments = Experiment.objects.all()
    
    experiment = get_object_or_404(experiments, id=id)
    title = experiment.title
    redirect_to = reverse("your_experiments")
    
    if experiment.owner != request.user:
        request.user.message_set.create(message="You can't delete objects that aren't yours")
        return HttpResponseRedirect(redirect_to)

    #if request.method == "POST" and request.POST["action"] == "delete":
    #experiment.delete()
    experiment.deleteObject()
    experiment.save()
    request.user.message_set.create(message=_("Successfully deleted experiment '%s'. You can find it in trash.") % title)
    
    return HttpResponseRedirect(redirect_to)



