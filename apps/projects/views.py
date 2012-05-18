from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from experiments.models import Experiment
from datasets.models import RDataset
from datafiles.models import Datafile

from django.conf import settings

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from django.db.models import Q
from friends.models import FriendshipManager
from projects.models import Project, ProjectMember
from projects.forms import ProjectForm, ProjectUpdateForm, AddUserForm, AddObjectForm, RemoveObjectForm

TOPIC_COUNT_SQL = """
SELECT COUNT(*)
FROM topics_topic
WHERE
    topics_topic.object_id = projects_project.id AND
    topics_topic.content_type_id = %s
"""
MEMBER_COUNT_SQL = """
SELECT COUNT(*)
FROM projects_projectmember
WHERE projects_projectmember.project_id = projects_project.id
"""

@login_required
def create(request, form_class=ProjectForm, template_name="projects/create.html"):
    project_form = form_class(request.POST or None)
    
    if project_form.is_valid():
        project = project_form.save(commit=False)
        project.creator = request.user
        project.save()
        project_member = ProjectMember(project=project, user=request.user)
        project.members.add(project_member)
        project_member.save()
        if notification:
            # @@@ might be worth having a shortcut for sending to all users
            notification.send(User.objects.all(), "projects_new_project",
                {"project": project}, queue=True)
        return HttpResponseRedirect(project.get_absolute_url())
    
    return render_to_response(template_name, {
        "project_form": project_form,
    }, context_instance=RequestContext(request))


@login_required
def projects(request, template_name="projects/projects.html"):
    
    projects = Project.objects.all().filter(private=False)
    
    search_terms = request.GET.get('search', '')
    if search_terms:
        projects = (projects.filter(name__icontains=search_terms) |
            projects.filter(description__icontains=search_terms))
    
    content_type = ContentType.objects.get_for_model(Project)
    
    projects = projects.extra(select=SortedDict([
        ('member_count', MEMBER_COUNT_SQL),
        ('topic_count', TOPIC_COUNT_SQL),
    ]), select_params=(content_type.id,))

    return render_to_response(template_name, {
        'projects': projects,
        'search_terms': search_terms,
    }, context_instance=RequestContext(request))


@login_required
def delete(request, group_slug=None, redirect_url=None):
    project = get_object_or_404(Project, slug=group_slug)
    if not redirect_url:
        redirect_url = reverse('your_projects')
    
    # @@@ eventually, we'll remove restriction that project.creator can't leave project but we'll still require project.members.all().count() == 1
    if (request.user.is_authenticated() and request.method == "POST" and
            request.user == project.creator and project.members.all().count() == 1):
        project.delete()
        request.user.message_set.create(message=_("Project %(project_name)s deleted.") % {"project_name": project.name})
        # no notification required as the deleter must be the only member
    
    return HttpResponseRedirect(redirect_url)


@login_required
def publish(request, group_slug=None, redirect_url=None):
    project = get_object_or_404(Project, slug=group_slug)
    if not redirect_url:
        redirect_url = reverse('project_list')
    
    if (request.user.is_authenticated() and request.method == "POST" and
            request.user == project.creator):
	if project.private == False:
	    project.private = True
	    project.save()
            request.user.message_set.create(message=_("Project %(project_name)s is now Private.") % {"project_name": project.name})
	else:
	    project.private = False
	    project.save()
            request.user.message_set.create(message=_("Project %(project_name)s is now Public.") % {"project_name": project.name})
    
    return HttpResponseRedirect(project.get_absolute_url())


@login_required
def your_projects(request, template_name="projects/your_projects.html"):

    projects = Project.objects.filter(member_users=request.user).order_by("name")

    content_type = ContentType.objects.get_for_model(Project)

    projects = projects.extra(select=SortedDict([
        ('member_count', MEMBER_COUNT_SQL),
        ('topic_count', TOPIC_COUNT_SQL),
    ]), select_params=(content_type.id,))

    return render_to_response(template_name, {
        "projects": projects,
    }, context_instance=RequestContext(request))


@login_required
def project(request, group_slug=None, form_class=ProjectUpdateForm, adduser_form_class=AddUserForm, 
        template_name="projects/project.html"):
    project = get_object_or_404(Project, slug=group_slug)
    is_creator = False

    if not request.user.is_authenticated():
        is_member = False
    else:
        is_member = project.user_is_member(request.user)

    action = request.POST.get("action")
    if request.user == project.creator:
        is_creator = True
        # update details handler    
        if action == "update":
            project_form = form_class(request.POST, instance=project)
            if project_form.is_valid():
                project = project_form.save()
        else:
            project_form = form_class(instance=project)

        # add new member handler
        if action == "add":
            adduser_form = adduser_form_class(request.POST, project=project)
            if adduser_form.is_valid():
                adduser_form.save(request.user)
                adduser_form = adduser_form_class(project=project) # clear form
        else:
            adduser_form = adduser_form_class(project=project)
    else:
        adduser_form = None
        project_form = None

    if request.user == project.creator or is_member:
        # assign new experiment handler
        if action == "new_experiment":
            exprt_form = AddObjectForm(request.POST, user=request.user, project=project, obj_type="experiment")
            if exprt_form.is_valid():
                sets = exprt_form.cleaned_data['objects_to_add']
                for s in sets:
                    s.add_linked_project(project)
                    s.save()
                request.user.message_set.create(message=_("Successfully added experiments to '%s'") % project.slug)
        else:
            exprt_form = AddObjectForm(user=request.user, project=project, obj_type="experiment")

        # remove experiments handler
        if action == "remove_experiments":
            exprt_remove_form = RemoveObjectForm(request.POST or None, user=request.user, project=project, obj_type="experiment")
            if exprt_remove_form.is_valid():
                ids = exprt_remove_form.cleaned_data['for_remove_choices'] 
                for exprt in Experiment.objects.filter(id__in=ids):
                    exprt.remove_linked_project(project)
                    exprt.save()
                request.user.message_set.create(message=_("Successfully removed selected experiments from '%s'") % project.slug)
        else:
            exprt_remove_form = RemoveObjectForm(user=request.user, project=project, obj_type="experiment")

        # assign new dataset handler
        if action == "new_dataset":
            dataset_form = AddObjectForm(request.POST, user=request.user, project=project, obj_type="dataset")
            if dataset_form.is_valid():
                sets = dataset_form.cleaned_data['objects_to_add']
                for s in sets:
                    s.add_linked_project(project)
                    s.save()
                request.user.message_set.create(message=_("Successfully added datasets to '%s'") % project.slug)
        else:
            dataset_form = AddObjectForm(user=request.user, project=project, obj_type="dataset")

        # remove datasets handler
        if action == "remove_datasets":
            dataset_remove_form = RemoveObjectForm(request.POST or None, user=request.user, project=project, obj_type="dataset")
            if dataset_remove_form.is_valid():
                ids = dataset_remove_form.cleaned_data['for_remove_choices'] 
                for dataset in RDataset.objects.filter(id__in=ids):
                    dataset.remove_linked_project(project)
                    dataset.save()
                request.user.message_set.create(message=_("Successfully removed selected datasets from '%s'") % project.slug)
        else:
            dataset_remove_form = RemoveObjectForm(user=request.user, project=project, obj_type="dataset")

        # assign new datafile handler
        if action == "new_datafile":
            datafile_form = AddObjectForm(request.POST, user=request.user, project=project, obj_type="datafile")
            if datafile_form.is_valid():
                sets = datafile_form.cleaned_data['objects_to_add']
                for s in sets:
                    s.add_linked_project(project)
                    s.save()
                request.user.message_set.create(message=_("File(s) were successfully added to '%s'") % project.slug)
        else:
            datafile_form = AddObjectForm(user=request.user, project=project, obj_type="datafile")

        # remove datafiles handler
        if action == "remove_datafiles":
            datafile_remove_form = RemoveObjectForm(request.POST or None, user=request.user, project=project, obj_type="datafile")
            if datafile_remove_form.is_valid():
                ids = datafile_remove_form.cleaned_data['for_remove_choices'] 
                for datafile in Datafile.objects.filter(id__in=ids):
                    datafile.remove_linked_project(project)
                    datafile.save()
                request.user.message_set.create(message=_("Successfully removed selected datafiles from '%s'") % project.slug)
        else:
            datafile_remove_form = RemoveObjectForm(user=request.user, project=project, obj_type="datafile")
    else:
        exprt_form = None
        exprt_remove_form = None
        dataset_form = None
        dataset_remove_form = None
        datafile_form = None
        datafile_remove_form = None

    experiments = project.experiment_set.all().filter(Q(current_state=10))
    experiments = filter(lambda x: x.is_accessible(request.user), experiments)
    datasets = project.rdataset_set.all().filter(Q(current_state=10))
    datasets = filter(lambda x: x.is_accessible(request.user), datasets)
    datafiles = project.datafile_set.all().filter(Q(current_state=10))
    datafiles = filter(lambda x: x.is_accessible(request.user), datafiles)

    return render_to_response(template_name, {
        "project_form": project_form,
        "adduser_form": adduser_form,
        "project": project,
        "group": project, # @@@ this should be the only context var for the project
        "is_member": is_member,
        "is_creator": is_creator,
        "experiments": experiments,
        "exprt_form": exprt_form,
        "exprt_remove_form": exprt_remove_form,
        "datasets": datasets,
        "dataset_form": dataset_form,
        "dataset_remove_form": dataset_remove_form,
        "datafiles": datafiles,
        "datafile_form": datafile_form,
        "datafile_remove_form": datafile_remove_form,
    }, context_instance=RequestContext(request))

