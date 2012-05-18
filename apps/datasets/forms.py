from django import forms
from django.forms import widgets
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.contrib.auth.models import User
from pinax.apps.projects.models import Project

from datasets.models import RDataset
from datafiles.models import Datafile
from experiments.models import Experiment
from fields.models import MMCFClearField

class NewRDatasetForm(forms.ModelForm):
    
    class Meta:
        model = RDataset
        fields = ['title', 'safety_level', 'caption', 'tags']

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(NewRDatasetForm, self).__init__(*args, **kwargs)
        choices = Project.objects.all().filter(Q(creator=user))
        self.fields['in_projects'] = MMCFClearField(queryset=choices)
        self.fields['in_projects'].label = "Related to projects"
        self.fields['in_projects'].help_text = 'Select related projects by typing a few letters in the box above. To remove all selected projects push <span id="clear_selection"><b style="cursor:pointer" onClick="autocompleteRemoveAll()">remove all</b></span>.'
        self.fields['safety_level'].help_text = "Nobody can see your PRIVATE datasets. FRIENDLY datasets can be viewed only by users you have assigned as friends. PUBLIC datasets available for every user."

# legacy form. Check and remove.
class RDatasetEditForm(forms.ModelForm):
    
    class Meta:
        model = RDataset
        exclude = ('date_added', 'owner', 'current_state')
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(RDatasetEditForm, self).__init__(*args, **kwargs)

class DeleteDatasetsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(DeleteDatasetsForm, self).__init__(*args, **kwargs)
        self.fields['set_choices'] = forms.MultipleChoiceField(
            choices=[(c.id, c.title) for c in RDataset.objects.filter(Q(current_state=10, owner=user))],
            widget=widgets.CheckboxSelectMultiple)

class DatasetShortEditForm(forms.ModelForm):
    
    class Meta:
        model = RDataset
        fields = ('title', 'caption', 'tags')
        
class PrivacyEditForm(forms.ModelForm):
    
    class Meta:
        model = RDataset
        fields = ('safety_level', 'shared_with')
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PrivacyEditForm, self).__init__(*args, **kwargs)
        choices = User.objects.exclude(id__exact=user.id)
        self.fields['shared_with'] = MMCFClearField(queryset=choices)


    # The classes below are legacy after implementation of 
    # the metadata section/property objects. So only applicable
    # for older objects in the database. Remove when no longer
    # required.
"""
class AddDatafileForm(forms.Form):
    datafiles = forms.ModelMultipleChoiceField(queryset=Datafile.objects.all().filter(current_state=10))
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        dataset = kwargs.pop('dataset')
        super(AddDatafileForm, self).__init__(*args, **kwargs)
	for_exclude = dataset.datafile_set.all().values_list("id", flat=True)
        choices = Datafile.objects.filter(owner=user, current_state=10).exclude(id__in=for_exclude)
        self.fields['datafiles'].queryset = choices

class RemoveDatafilesForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        dataset = kwargs.pop('dataset')
        super(RemoveDatafilesForm, self).__init__(*args, **kwargs)
	values = dataset.datafile_set.all().filter(Q(current_state=10))
	values = filter(lambda x: x.is_accessible(user), values)
        self.fields['dfile_choices'] = forms.MultipleChoiceField(
            choices=[(c.id, c.title) for c in values], required=False,
            widget=widgets.CheckboxSelectMultiple)
"""
