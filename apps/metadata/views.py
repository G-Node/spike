from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, get_host, QueryDict, HttpResponse
from django.template import RequestContext
#from django.db.models import Q
#from django.http import Http404
from django.core.urlresolvers import reverse
#from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime

from experiments.models import Experiment
from datasets.models import RDataset
from datafiles.models import Datafile
from timeseries.models import TimeSeries
from metadata.forms import AddSectionForm, AddPropertyForm, EditPropertyForm, LinkDatasetForm, LinkDatafileForm, LinkTSForm, importOdML
from metadata.models import Section, Property


@login_required # ajax-only
def section_add(request, template_name="metadata/add.html"):
    parent_type = 0
    parent = None
    section_id = None
    # parent types - "1" - Experiment; "2" - Dataset; "3" - Section; "4" - Time Series; "5" - Datafile
    # don't ask why they are in this order, this method needs optimization
    if request.method == 'POST' and request.POST.get("action") == "section_add":
        parent_id = request.POST.get("parent_id")
        section_title = request.POST.get("new_name")
        parent_type = request.POST.get("parent_type")
        if parent_type == "3":
            parent = get_object_or_404(Section, id=parent_id)
        if parent_type == "1":
            parent = get_object_or_404(Experiment, id=parent_id)
        if parent_type == "2":
            parent = get_object_or_404(RDataset, id=parent_id)
        if parent_type == "4":
            parent = get_object_or_404(TimeSeries, id=parent_id)
        if parent_type == "5":
            parent = get_object_or_404(Datafile, id=parent_id)

        # identify the position in the tree. ahhh doesn't work here
        #tree_pos = parent._get_next_tree_pos()
        sec_childs = parent.section_set.all().order_by("-tree_position")
        if sec_childs:
            tree_pos = int(sec_childs.all()[0].tree_position) + 1
        else:
            tree_pos = 1

        if parent_type == "3":
            if parent.does_belong_to(request.user):
                section = Section(title=section_title, parent_section=parent, tree_position=tree_pos)
                section.save()
                section_id = section.id
        elif parent.owner == request.user:
            if parent_type == "1":
                section = Section(title=section_title, parent_exprt=parent, tree_position=tree_pos)
            if parent_type == "2":
                section = Section(title=section_title, parent_dataset=parent, tree_position=tree_pos)
            if parent_type == "4":
                section = Section(title=section_title, parent_timeseries=parent, tree_position=tree_pos)
            if parent_type == "5":
                section = Section(title=section_title, parent_datafile=parent, tree_position=tree_pos)
            if section:
                section.save()
                section_id = section.id
    else:
        section_id = None
    return render_to_response(template_name, {
        "section_id": section_id,
        }, context_instance=RequestContext(request))


@login_required # ajax-only
def section_delete(request, template_name="metadata/dummy.html"):
    status = False
    if request.method == 'POST' and request.POST.get("action") == "section_delete":
        section_id = request.POST.get("node_id")
        section = get_object_or_404(Section, id=section_id)
        if section.does_belong_to(request.user):
            section.deleteObject()
            status = True
    return render_to_response(template_name, {
        "status": status,
        }, context_instance=RequestContext(request))


@login_required # ajax-only
def section_edit(request, template_name="metadata/dummy.html"):
    status = False
    if request.method == 'POST' and request.POST.get("action") == "section_edit":
        new_title = request.POST.get("new_name")
        section_id = request.POST.get("new_id")
        section = get_object_or_404(Section, id=section_id)
        if section.does_belong_to(request.user):
            section.rename(new_title)
            status = True
    return render_to_response(template_name, {
        "status": status,
        }, context_instance=RequestContext(request))


@login_required # ajax-only
def section_move(request, template_name="metadata/move_copy.html"):
    status = 0
    if request.method == 'POST' and request.POST.get("action") == "section_move":
        selected_id = request.POST.get("selected_id")
        reference_id = request.POST.get("reference_id")
        pos_type = request.POST.get("pos_type")
        section = get_object_or_404(Section, id=selected_id)
        ref_section = get_object_or_404(Section, id=reference_id)
        if section.does_belong_to(request.user):
            if pos_type == "inside":
                section.clean_parent()
                section.parent_section = ref_section
                section.tree_position = 1
                section.save()
                status = 1
            elif pos_type == "after":
                parent = ref_section.get_parent()
                if parent:
                    section.tree_position = ref_section.tree_position + 1
                    if isinstance(parent, Section):
                        secs = parent.section_set.filter(tree_position__gt=ref_section.tree_position)
                        section.parent_section = parent
                    elif isinstance(parent, Experiment):
                        secs = Section.objects.filter(parent_exprt=parent).filter(tree_position__gt=ref_section.tree_position)
                        section.clean_parent()
                        section.parent_exprt = parent
                    elif isinstance(parent, RDataset):
                        secs = Section.objects.filter(parent_dataset=parent).filter(tree_position__gt=ref_section.tree_position)
                        section.clean_parent()
                        section.parent_dataset = parent
                    elif isinstance(parent, Datafile):
                        secs = Section.objects.filter(parent_datafile=parent).filter(tree_position__gt=ref_section.tree_position)
                        section.clean_parent()
                        section.parent_datafile = parent
                    elif isinstance(parent, TimeSeries):
                        secs = Section.objects.filter(parent_timeseries=parent).filter(tree_position__gt=ref_section.tree_position)
                        section.clean_parent()
                        section.parent_timeseries = parent
                    else:
                        secs = []
                    # moving positions
                    for sec in secs:
                        sec.increaseTreePos()
                    section.save()
                    status = 1
            elif pos_type == "before":
                parent = ref_section.get_parent()
                if parent:
                    section.tree_position = ref_section.tree_position
                    if isinstance(parent, Section):
                        secs = parent.section_set.filter(tree_position__gte=ref_section.tree_position)
                        section.parent_section = parent
                    elif isinstance(parent, Experiment):
                        secs = Section.objects.filter(parent_exprt=parent).filter(tree_position__gte=ref_section.tree_position)
                        section.clean_parent()
                        section.parent_exprt = parent
                    elif isinstance(parent, RDataset):
                        secs = Section.objects.filter(parent_dataset=parent).filter(tree_position__gte=ref_section.tree_position)
                        section.clean_parent()
                        section.parent_dataset = parent
                    elif isinstance(parent, Datafile):
                        secs = Section.objects.filter(parent_datafile=parent).filter(tree_position__gte=ref_section.tree_position)
                        section.clean_parent()
                        section.parent_datafile = parent
                    elif isinstance(parent, TimeSeries):
                        secs = Section.objects.filter(parent_timeseries=parent).filter(tree_position__gte=ref_section.tree_position)
                        section.clean_parent()
                        section.parent_timeseries = parent
                    else:
                        secs = []
                    # moving positions
                    for sec in secs:
                        sec.increaseTreePos()
                    section.save()
                    status = 1
    return render_to_response(template_name, {
        "status": status,
        }, context_instance=RequestContext(request))


@login_required # ajax-only
def section_copy(request, template_name="metadata/move_copy.html"):
    status = 0
    prnt = 1
    if request.method == 'POST' and request.POST.get("action") == "section_copy":
        selected_id = request.POST.get("selected_id")
        reference_id = request.POST.get("reference_id")
        pos_type = request.POST.get("pos_type")
        section = get_object_or_404(Section, id=selected_id)
        ref_section = get_object_or_404(Section, id=reference_id)
        if section.does_belong_to(request.user) or (section.is_template and (section.user_custom is None)) or (section.is_template and (section.user_custom == request.user)):
            if pos_type == "inside":
                status = ref_section.copy_section(section, 1)
            elif pos_type == "after":
                parent = ref_section.get_parent()
                if parent:
                    if isinstance(parent, Section):
                        secs = parent.section_set.filter(tree_position__gt=ref_section.tree_position)
                        prnt = 0
                    elif isinstance(parent, Experiment):
                        secs = Section.objects.filter(parent_exprt=parent).filter(tree_position__gt=ref_section.tree_position)
                    elif isinstance(parent, RDataset):
                        secs = Section.objects.filter(parent_dataset=parent).filter(tree_position__gt=ref_section.tree_position)
                    elif isinstance(parent, Datafile):
                        secs = Section.objects.filter(parent_datafile=parent).filter(tree_position__gt=ref_section.tree_position)
                    elif isinstance(parent, TimeSeries):
                        secs = Section.objects.filter(parent_timeseries=parent).filter(tree_position__gt=ref_section.tree_position)
                    else:
                        secs = []
                    # moving positions
                    for sec in secs:
                        sec.increaseTreePos()
                    if prnt:
                        # parent is "complex" oblect - Experiment, Dataset etc.
                        status = ref_section.copy_section(section, ref_section.tree_position + 1, True)
                    else:
                        # parent is "simple" oblect - Section
                        status = parent.copy_section(section, ref_section.tree_position + 1)
                else:
                    status = -1
            elif pos_type == "before":
                parent = ref_section.get_parent()
                if parent:
                    if isinstance(parent, Section):
                        secs = parent.section_set.filter(tree_position__gte=ref_section.tree_position)
                        prnt = 0
                    elif isinstance(parent, Experiment):
                        secs = Section.objects.filter(parent_exprt=parent).filter(tree_position__gte=ref_section.tree_position)
                    elif isinstance(parent, RDataset):
                        secs = Section.objects.filter(parent_dataset=parent).filter(tree_position__gte=ref_section.tree_position)
                    elif isinstance(parent, Datafile):
                        secs = Section.objects.filter(parent_datafile=parent).filter(tree_position__gte=ref_section.tree_position)
                    elif isinstance(parent, TimeSeries):
                        secs = Section.objects.filter(parent_timeseries=parent).filter(tree_position__gte=ref_section.tree_position)
                    else:
                        secs = []
                    # moving positions
                    for sec in secs:
                        sec.increaseTreePos()
                    if prnt:
                        # parent is "complex" oblect - Experiment, Dataset etc.
                        status = ref_section.copy_section(section, ref_section.tree_position, True)
                    else:
                        # parent is "simple" oblect - Section
                        status = parent.copy_section(section, ref_section.tree_position)
                else:
                    status = -1
    return render_to_response(template_name, {
        "status": status,
        }, context_instance=RequestContext(request))


@login_required # ajax-only
def properties_list(request, id, template_name="metadata/properties_list.html"):
    section = get_object_or_404(Section, id=id)
    if not section.is_accessible(request.user):
        raise Http404
    properties = section.get_active_properties(request.user)
    datafiles = section.get_active_datafiles(request.user)
    datasets = section.get_active_datasets(request.user)
    timeseries = section.get_active_timeseries(request.user)
    is_owner = (section.get_owner() == request.user)
    return render_to_response(template_name, {
        "section": section,
        "is_owner": is_owner,
        "properties": properties,
        "datafiles": datafiles,
        "datasets": datasets,
        "timeseries": timeseries,
        }, context_instance=RequestContext(request))
        


@login_required # ajax-only
def property_add(request, id, property_form_class=AddPropertyForm, template_name="metadata/property_add.html"):
    property_id = 0
    prop_form = property_form_class(request.POST, auto_id='id_add_form_%s')
    if request.method == 'POST' and prop_form.is_valid():
        property_title = request.POST.get("prop_title")
        property_value = request.POST.get("prop_value")
        section = get_object_or_404(Section, id=id)
        if request.POST.get("action") == "property_add" and section.does_belong_to(request.user):
            new_property = Property(prop_title=property_title, prop_value=property_value, prop_parent_section=section)
            new_property.save()
            property_id = new_property.id
    return render_to_response(template_name, {
        "property_id": property_id,
        "prop_add_form": prop_form,
        }, context_instance=RequestContext(request))


@login_required # ajax-only
def property_delete(request, template_name="metadata/dummy.html"):
    status = False
    if request.method == 'POST' and request.POST.get("action") == "property_delete":
        property_id = request.POST.get("prop_id")
        prop = get_object_or_404(Property, id=property_id)
        if prop.does_belong_to(request.user):
            prop.deleteObject()
            status = True
    return render_to_response(template_name, {
        "status": status,
        }, context_instance=RequestContext(request))


@login_required # ajax-only
def property_edit(request, id, form_class=EditPropertyForm, template_name="metadata/property_edit.html"):
    property_form = None
    property_id = id
    upd_result = 0
    sel_property = get_object_or_404(Property, id=id)

    if request.method == "POST" and request.POST.get("action") == 'update_form':
        property_form = form_class(request.POST, auto_id='id_edit_form_%s', prop=sel_property)
        if property_form.is_valid() and sel_property.does_belong_to(request.user):
            #sel_property = property_form.save(commit=False)
            sel_property.update(request.POST.get("prop_title"), request.POST.get("prop_value"), 
                request.POST.get("prop_description"), request.POST.get("prop_comment"), request.POST.get("prop_definition"))
            sel_property.save()
            property_id = sel_property.id
            upd_result = property_id
    elif request.method == "POST" and request.POST.get("action") == 'get_form':
        property_form = form_class(auto_id='id_edit_form_%s', instance=sel_property, prop=sel_property)
    
    return render_to_response(template_name, {
        "upd_result": upd_result,
        "property_id": property_id,
        "prop_edit_form": property_form,
    }, context_instance=RequestContext(request))


@login_required # ajax-only
def object_link(request, id, template_name="metadata/object_link.html"):
    section_id = 0
    obj_type = None
    # transform dataset<number> into <datasets> querydict to 
    # easy create a form
    d_dict = ""
    f_dict = ""
    t_dict = ""
    for key, value in request.POST.items():
        if str(key).find("dataset") == 0:
            d_dict += "datasets=" + value + "&"
        if str(key).find("datafile") == 0:
            f_dict += "datafiles=" + value + "&"
        if str(key).find("timeseries") == 0:
            t_dict += "timeseries=" + value + "&"
    if request.path.find("dataset_link") > 0:
        form = LinkDatasetForm(QueryDict(d_dict), auto_id='id_dataset_form_%s', user=request.user)
        obj_type = "dataset"
    elif request.path.find("datafile_link") > 0:
        form = LinkDatafileForm(QueryDict(f_dict), auto_id='id_datafile_form_%s', user=request.user)
        obj_type = "datafile"
    elif request.path.find("timeseries_link") > 0:
        form = LinkTSForm(QueryDict(t_dict), auto_id='id_timeseries_form_%s', user=request.user)
        obj_type = "timeseries"
    else:
        form = LinkDatasetForm(auto_id='id_dataset_form_%s', user=request.user)
        obj_type = "dataset"

    if request.method == 'POST' and form.is_valid():
        section = get_object_or_404(Section, id=id)
        if request.POST.get("action").find("_link") > 0 and section.does_belong_to(request.user):
            if obj_type == "dataset":
                sets = form.cleaned_data['datasets']
            elif obj_type == "datafile":
                sets = form.cleaned_data['datafiles']
            elif obj_type == "timeseries":
                sets = form.cleaned_data['timeseries']
            else:
                sets = None
            for s in sets:
                section.addLinkedObject(s, obj_type)
            section.save()
            section_id = section.id
    return render_to_response(template_name, {
        "section_id": section_id,
        "object_form": form,
        "obj": obj_type,
        }, context_instance=RequestContext(request))


@login_required # ajax-only
def remove_object(request, template_name="metadata/dummy.html"):
    status = False
    if request.method == 'POST' and request.POST.get("action") == "remove_dataset":
        dataset = get_object_or_404(RDataset, id=request.POST.get("dataset_id"))
        section = get_object_or_404(Section, id=request.POST.get("section_id"))
        if dataset.owner == request.user:
            section.removeLinkedObject(dataset, "dataset")
            section.save()
            status = True
    elif request.method == 'POST' and request.POST.get("action") == "remove_datafile":
        datafile = get_object_or_404(Datafile, id=request.POST.get("datafile_id"))
        section = get_object_or_404(Section, id=request.POST.get("section_id"))
        if datafile.owner == request.user:
            section.removeLinkedObject(datafile, "datafile")
            section.save()
            status = True
    elif request.method == 'POST' and request.POST.get("action") == "remove_timeseries":
        timeseries = get_object_or_404(TimeSeries, id=request.POST.get("timeseries_id"))
        section = get_object_or_404(Section, id=request.POST.get("section_id"))
        if timeseries.owner == request.user:
            section.removeLinkedObject(timeseries, "timeseries")
            section.save()
            status = True
    return render_to_response(template_name, {
        "status": status,
        }, context_instance=RequestContext(request))


@login_required # ajax-only
def import_odml(request, id, template_name="metadata/import_odml.html"):
    data = -1
    section_id = 0
    file_id = request.POST.get("file_id")
    form = importOdML(QueryDict("files=" + str(file_id)), auto_id='id_odml_form_%s', user=request.user)
    section = get_object_or_404(Section, id=id)
    if request.method == 'POST' and form.is_valid():
        if request.POST.get("action") == "import_odml" and section.does_belong_to(request.user):
            f_id = form.cleaned_data['files']
            f = open(get_object_or_404(Datafile, id=f_id.id).raw_file.path, "r")
            section._import_xml(f)
            data = section.get_tree(id_only=True)
            section_id = section.id
            f.close()
    return render_to_response(template_name, {
        "section_id": section_id,
        "object_form": form,
        "obj": "odml",
        "data": data, # id values of newly created sections for tree update
        }, context_instance=RequestContext(request))


@login_required
def export_odml(request, id, template_name="metadata/export_odml.xml"):
    section = get_object_or_404(Section, id=id)
    response = HttpResponse(section._export_xml(), mimetype="application/xml")
    response['Content-Disposition'] = 'attachment; filename=odml.xml'
    return response

    #return render_to_response(template_name, {
    #    "xml_data": section._export_xml(),
    #    }, context_instance=RequestContext(request))


