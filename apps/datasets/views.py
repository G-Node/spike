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

#from photologue.models import *
from datasets.models import RDataset
from datafiles.models import Datafile
from metadata.models import Section
from datasets.forms import NewRDatasetForm, RDatasetEditForm, DeleteDatasetsForm, DatasetShortEditForm, PrivacyEditForm
from metadata.forms import AddPropertyForm, LinkDatafileForm, LinkTSForm, importOdML
from metadata.models import Section

@login_required
def create(request, form_class=NewRDatasetForm, template_name="datasets/new.html"):
    """
    create new Dataset form
    """
    
    dataset_form = form_class(request.user)
    if request.method == 'POST':
        if request.POST.get("action") == "create":
            dataset_form = form_class(request.user, request.POST)
            if dataset_form.is_valid():
                dataset = dataset_form.save(commit=False)
                dataset.owner = request.user
                dataset.save()
                dataset_form.save_m2m()

                # create default section to add files
                section = Section(title="link files here", parent_dataset=dataset, tree_position=1)
                section.save()
                request.user.message_set.create(message=_("Successfully created dataset '%s'") % dataset.title)
                include_kwargs = {"id": dataset.id}
                #redirect_to = reverse("dataset_details", kwargs=include_kwargs)
                #return HttpResponseRedirect(redirect_to)
                
                return HttpResponseRedirect(dataset.get_absolute_url())

    return render_to_response(template_name, {
        "dataset_form": dataset_form,
    }, context_instance=RequestContext(request))


@login_required
def yourdatasets(request, template_name="datasets/your_datasets.html"):
    """
    datasets for the currently authenticated user
    """
    datasets = RDataset.objects.filter(owner=request.user, current_state=10)
    datasets = datasets.order_by("-date_added")
    set_objects_form = DeleteDatasetsForm(request.POST or None, user=request.user)
    
    action = request.POST.get("action")
    if request.method == 'POST' and action == "delete":
        if set_objects_form.is_valid():
            ids = set_objects_form.cleaned_data['set_choices'] # [u'39', u'20', u'18']
            for rdataset in RDataset.objects.filter(id__in=ids):
                if rdataset.owner == request.user:
                    rdataset.deleteObject()
                    rdataset.save()
                else:
                    raise Http404
            request.user.message_set.create(message=("Successfully deleted the requested datasets. Files attached to a dataset are still available"))
            redirect_to = reverse("your_datasets")
            return HttpResponseRedirect(redirect_to)
            
    return render_to_response(template_name, {
        "datasets": datasets,
    }, context_instance=RequestContext(request))


@login_required
def alldatasets(request, template_name="datasets/all.html"):
    """
    this method is oficially not used 
    """
    
    datasets = RDataset.objects.filter(Q(safety_level=1), Q(current_state=10)
        #Q(securitylevel=3, owner=request.user)
    )
    
    datasets = datasets.order_by("-date_added")
    
    return render_to_response(template_name, {
        "datasets": datasets,
    }, context_instance=RequestContext(request))


@login_required
def datasetdetails(request, id, form_class=DatasetShortEditForm, privacy_form_class=PrivacyEditForm, 
    datafile_form_class=LinkDatafileForm, timeseries_form_class=LinkTSForm, property_form_class1=AddPropertyForm, 
    template_name="datasets/details.html"):

   # change here !!! RDataset.objects.get(id__exact=id) + raise Http404 if nothing
    datasets = RDataset.objects.all()
    dataset = get_object_or_404(datasets, id=id)
    datasets = None
    
    # security handler
    if not dataset.is_accessible(request.user):
        dataset = None
        raise Http404

    action = request.POST.get("action")

    # edit details handler
    if request.user == dataset.owner and action == "details_update":
        dataset_form = form_class(request.POST, instance=dataset)
        if dataset_form.is_valid():
            dataset = dataset_form.save()
    else:
        dataset_form = form_class(instance=dataset)
    
    # edit privacy handler    
    if request.user == dataset.owner and action == "privacy_update":
        privacy_form = privacy_form_class(request.user, request.POST, instance=dataset)
        if privacy_form.is_valid():
            dataset = privacy_form.save()
    else:
        privacy_form = privacy_form_class(user=request.user, instance=dataset)

    # templates for metadata. can't move to state_mashine due to import error
    metadata_defaults = []
    for section in Section.objects.filter(current_state=10, is_template=True):
        if not section.parent_section:
            metadata_defaults.append(section.get_tree())
    for section in Section.objects.filter(current_state=10, user_custom=dataset.owner):
        if not section.parent_section:
            metadata_defaults.append(section.get_tree())

    prop_add_form = property_form_class1(auto_id='id_add_form_%s')
    datafile_link_form = datafile_form_class(auto_id='id_datafile_form_%s', user=request.user)
    timeseries_link_form = timeseries_form_class(auto_id='id_timeseries_form_%s', user=request.user)
    odml_import_form = importOdML(auto_id='id_odml_form_%s', user=request.user)

    # get the parent experiments to which dataset is linked to
    exprts = []
    sections = Section.objects.filter(current_state=10)
    sections = filter(lambda x: x.has_dataset(dataset.id), sections)
    for section in sections:
        rt = section.get_root()
        if not rt in exprts:
            exprts.append(rt)

    # get the id of the first available section to select it in the tree (onload)
    first_section_id = request.GET.get("section_id")
    if not first_section_id:
        sections = dataset.section_set.filter(current_state=10).order_by("tree_position")
        if sections:
            first_section_id = sections[0].id

    return render_to_response(template_name, {
        "dataset": dataset,
        "metadata_defaults": metadata_defaults,
        "dataset_form": dataset_form,
        "privacy_form": privacy_form,
        "prop_add_form": prop_add_form,
        "datafile_link_form": datafile_link_form,
        "timeseries_link_form": timeseries_link_form,
        "odml_import_form": odml_import_form,
        "exprts": exprts,
        "first_section_id": first_section_id,
    }, context_instance=RequestContext(request))


@login_required
def edit(request, id, form_class=RDatasetEditForm, template_name="datasets/edit.html"):
    
    datasets = RDataset.objects.all()
    
    dataset = get_object_or_404(datasets, id=id)

    if request.method == "POST":
        if dataset.owner != request.user:
            request.user.message_set.create(message="You can't edit datasets that aren't yours")
            
            include_kwargs = {"id": dataset.id}
            redirect_to = reverse("dataset_details", kwargs=include_kwargs)
            return HttpResponseRedirect(reverse('dataset_details', args=(dataset.id,)))

        if request.POST["action"] == "update":
            dataset_form = form_class(request.user, request.POST, instance=dataset)
            if dataset_form.is_valid():
                datasetobj = dataset_form.save(commit=False)
                datasetobj.save()
                dataset_form.save_m2m()
                
                request.user.message_set.create(message=_("Successfully updated dataset '%s'") % dataset.title)
                
                include_kwargs = {"id": dataset.id}
                redirect_to = reverse("dataset_details", kwargs=include_kwargs)
                return HttpResponseRedirect(redirect_to)
        else:
            dataset_form = form_class(instance=dataset)

    else:
        dataset_form = form_class(instance=dataset)

    return render_to_response(template_name, {
        "dataset_form": dataset_form,
        "dataset": dataset,
    }, context_instance=RequestContext(request))


@login_required
def datasetDelete(request, id):
    
    datasets = RDataset.objects.all()
    
    dataset = get_object_or_404(datasets, id=id)
    title = dataset.title
    
    redirect_to = reverse("your_datasets")
    
    if dataset.owner != request.user:
        request.user.message_set.create(message="You can't delete datasets that aren't yours")
        return HttpResponseRedirect(redirect_to)

    #if request.method == "POST" and request.POST["action"] == "delete":
    #dataset.deleteObject()
    dataset.deleteObject()
    dataset.save()
    request.user.message_set.create(message=_("Successfully deleted dataset '%s'. Files attached to a dataset are still available") % title)
    
    return HttpResponseRedirect(redirect_to)
