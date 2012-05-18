from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe
from experiments.models import Experiment
from datasets.models import RDataset
from datafiles.models import Datafile
from django.db.models import Q

class RestoreExperimentsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(RestoreExperimentsForm, self).__init__(*args, **kwargs)
        self.fields['exp_choices'] = forms.MultipleChoiceField(
            choices=[(c.id, c.title) for c in Experiment.objects.filter(Q(current_state=20, owner=user))],
            widget=widgets.CheckboxSelectMultiple)

class RestoreDatasetsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(RestoreDatasetsForm, self).__init__(*args, **kwargs)
        self.fields['set_choices'] = forms.MultipleChoiceField(
            choices=[(c.id, c.title) for c in RDataset.objects.filter(Q(current_state=20, owner=user))],
            widget=widgets.CheckboxSelectMultiple)
        
class RestoreFilesForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(RestoreFilesForm, self).__init__(*args, **kwargs)
        self.fields['fil_choices'] = forms.MultipleChoiceField(
            choices=[(c.id, c.title) for c in Datafile.objects.filter(Q(current_state=20, owner=user))],
            widget=widgets.CheckboxSelectMultiple)