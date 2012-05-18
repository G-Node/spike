from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import widgets
from django.db.models import Q
from django.contrib.auth.models import User

from projects.models import Project, ProjectMember
from experiments.models import Experiment
from datasets.models import RDataset
from datafiles.models import Datafile
from django.conf import settings

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

# @@@ we should have auto slugs, even if suggested and overrideable

class ProjectForm(forms.ModelForm):
    name = forms.CharField(label="Title")
    slug = forms.SlugField(max_length=20,
        help_text = _("a short name consisting only of letters, numbers, underscores and hyphens, which is used as an identifier to represent the project. The slug cannot be changed later."))

    def clean_slug(self):
        if Project.objects.filter(slug__iexact=self.cleaned_data["slug"]).count() > 0:
            raise forms.ValidationError(_("A project already exists with that slug."))
        return self.cleaned_data["slug"].lower()
    
    def clean_name(self):
        if Project.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
            raise forms.ValidationError(_("A project already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Project
        fields = ('name', 'slug', 'description')


# @@@ is this the right approach, to have two forms where creation and update fields differ?

class ProjectUpdateForm(forms.ModelForm):
    
    def clean_name(self):
        if Project.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
            if self.cleaned_data["name"] == self.instance.name:
                pass # same instance
            else:
                raise forms.ValidationError(_("A project already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Project
        fields = ('name', 'description')


class AddUserForm(forms.Form):
    
    #recipient = forms.CharField(label=_(u"User"))
    
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project")
        super(AddUserForm, self).__init__(*args, **kwargs)
        p_members = ProjectMember.objects.filter(project=self.project)
        for_exclude = []
        # alternative way to get a list of users - doesn't work
        #for_exclude = User.objects.filter(id__iexact=p_members.user)#.values_list("id", flat=True)
        for pmem in p_members:
            for_exclude.append(pmem.user.id)
        choices = User.objects.exclude(id__in=for_exclude)
        self.fields['recipient'] = forms.ModelMultipleChoiceField(queryset=choices)
    
    def save(self, user):
        new_members = self.cleaned_data['recipient']
        str_members = ""
        for member in new_members:
            project_member = ProjectMember(project=self.project, user=member)
            project_member.save()
            self.project.members.add(project_member)
            str_members += str(", " + project_member.user.username)
        if notification:
            str_members = str_members[2:]
            notification.send(self.project.member_users.all(), "projects_new_member", {"new_member": str_members, "project": self.project})
            #notification.send([new_member], "projects_added_as_member", {"adder": user, "project": self.project})
        user.message_set.create(message="added %s to project" % str_members)

class AddObjectForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        project = kwargs.pop('project')
        obj_type = kwargs.pop('obj_type')
        super(AddObjectForm, self).__init__(*args, **kwargs)
        if obj_type == "experiment":
            for_exclude = project.experiment_set.all().values_list("id", flat=True)
            choices = Experiment.objects.filter(owner=user, current_state=10).exclude(id__in=for_exclude)
        elif obj_type == "dataset":
            for_exclude = project.rdataset_set.all().values_list("id", flat=True)
            choices = RDataset.objects.filter(owner=user, current_state=10).exclude(id__in=for_exclude)
        elif obj_type == "datafile":
            for_exclude = project.datafile_set.all().values_list("id", flat=True)
            choices = Datafile.objects.filter(owner=user, current_state=10).exclude(id__in=for_exclude)
        else:
            choices = None
        self.fields['objects_to_add'] = forms.ModelMultipleChoiceField(queryset=choices)

class RemoveObjectForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        project = kwargs.pop('project')
        obj_type = kwargs.pop('obj_type')
        super(RemoveObjectForm, self).__init__(*args, **kwargs)
        if obj_type == "experiment":
            values = project.experiment_set.all().filter(Q(current_state=10))
        elif obj_type == "dataset":
            values = project.rdataset_set.all().filter(Q(current_state=10))
        elif obj_type == "datafile":
            values = project.datafile_set.all().filter(Q(current_state=10))
        else:
            values = []
        values = filter(lambda x: x.is_accessible(user), values)
        self.fields['for_remove_choices'] = forms.MultipleChoiceField(
            choices=[(c.id, c.title) for c in values], required=False,
            widget=widgets.CheckboxSelectMultiple)


