from django import forms
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.forms import widgets
from django.db.models import Q
from django.contrib.auth.models import User

from datafiles.models import Datafile
from fields.models import MMCFClearField

class NewDatafileForm(forms.ModelForm):
    
    class Meta:
        model = Datafile
        fields = ['safety_level', 'raw_file', 'caption', 'tags']

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(NewDatafileForm, self).__init__(*args, **kwargs)
        self.fields['safety_level'].help_text = "Nobody can see your PRIVATE files. FRIENDLY files can be viewed only by users you have assigned as friends. PUBLIC files are available by every user. The privacy level can be modified later, where files can also be shared on an individual basis."
        self.fields['raw_file'].help_text = "Please select a file up to 2GB size. Soon you'll be able to upload without this restrictions."

class DatafileEditForm(forms.ModelForm):
    
    class Meta:
        model = Datafile
        exclude = ('date_added', 'owner', 'current_state', 'raw_file')
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(DatafileEditForm, self).__init__(*args, **kwargs)

class DeleteDatafileForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(DeleteDatafileForm, self).__init__(*args, **kwargs)
        self.fields['set_choices'] = forms.MultipleChoiceField(
            choices=[(c.id, c.title) for c in Datafile.objects.filter(Q(current_state=10, owner=user))],
            widget=widgets.CheckboxSelectMultiple)

class DatafileShortEditForm(forms.ModelForm):
    
    class Meta:
        model = Datafile
        fields = ('title', 'caption', 'tags')
        
class PrivacyEditForm(forms.ModelForm):
    
    class Meta:
        model = Datafile
        fields = ('safety_level', 'shared_with')
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PrivacyEditForm, self).__init__(*args, **kwargs)
        choices = User.objects.exclude(id__exact=user.id)
        self.fields['shared_with'] = MMCFClearField(queryset=choices)


