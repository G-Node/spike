import re
from django import forms
from django.forms import widgets
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings
from django.template.defaultfilters import filesizeformat

from experiments.models import Experiment
from datasets.models import RDataset
from datafiles.models import Datafile
from timeseries.models import TimeSeries
from fields.models import MMCFClearField

def reg_csv():
    #regex = re.compile('^[\d+\.\d*,]+$')
    return re.compile(r'''
        \s*                # Any whitespace.
        (                  # Start capturing here.
          [^,"']+?         # Either a series of non-comma non-quote characters.
          |                # OR
          "(?:             # A double-quote followed by a string of characters...
              [^"\\]|\\.   # That are either non-quotes or escaped...
           )*              # ...repeated any number of times.
          "                # Followed by a closing double-quote.
          |                # OR
          '(?:[^'\\]|\\.)*'# Same as above, for single quotes.
        )                  # Done capturing.
        \s*                # Allow arbitrary space before the comma.
        (?:,|$)            # Followed by a comma or the end of a string.
        ''', re.VERBOSE)

class AddTSfromFieldForm(forms.ModelForm):

    def clean_data(self):
        r = reg_csv()
        values = r.findall(self.cleaned_data["data"])
        cleaned_data = ''
        for value in values:
            try:
                a = float(value)
                cleaned_data += ', ' + str(a)
            except:
                raise forms.ValidationError(_('The data given is not a set of comma-separated float / integer values. Please check your input: %s') % value)
        if len(cleaned_data) > 0:
            cleaned_data = cleaned_data[2:]
        return cleaned_data

    class Meta:
        model = TimeSeries
        fields = ['data', 'data_type', 'time_step', 'time_step_items']

    def __init__(self, *args, **kwargs):
        super(AddTSfromFieldForm, self).__init__(*args, **kwargs)
        self.fields['data'].help_text = 'Please insert comma-separated values (floats or integers) in the field. Example: "0.8386, -0.8372, 0.839, -0.84, 0.8389".'
        self.fields['data_type'].help_text = 'ANALOG - typically a voltage trace. SPIKES - typically a sequence of "0, 0, 0, 1, 0", representing spike times.'


class AddTSfromFileForm(forms.ModelForm):
    datafile = forms.ModelChoiceField(queryset=Datafile.objects.all().filter(current_state=10))
    selection = forms.ChoiceField(label='Organize', required=False)
    my_datasets = forms.ModelChoiceField(queryset=RDataset.objects.all().filter(current_state=10), required=False)
    new_dataset = forms.CharField(label='New dataset name', required=False)
    
    def clean_datafile(self):
        datafile = self.cleaned_data["datafile"]
        r = reg_csv()
        res = []
        d = settings.MEDIA_ROOT + str(datafile.raw_file)
        if datafile.raw_file.size > settings.MAX_FILE_PROCESSING_SIZE:
            raise forms.ValidationError(_('The file size exceeds the limit: %s') % filesizeformat(datafile.raw_file.size))
        else:
            #with open(settings.MEDIA_ROOT + str(datafile.raw_file), 'r') as f:
            try:
                f = open(settings.MEDIA_ROOT + str(datafile.raw_file), 'r')
            except:
                raise forms.ValidationError(_('The given datafile cannot be opened for reading. Please check the file has ASCII formatting.'))
            read_data = f.readline()
            while read_data:
                values = r.findall(read_data)
                cleaned_data = ''
                for value in values:
                    try:
                        a = float(value)
                        cleaned_data += ', ' + str(a)
                    except:
                        raise forms.ValidationError(_('The data given is not a set of comma-separated float / integer values. Please check your input: %s') % value)
                if len(cleaned_data) > 0:
                    cleaned_data = cleaned_data[2:]
                res.append([cleaned_data])
                read_data = f.readline()
            f.close()
            return res

    class Meta:
        model = TimeSeries
        fields = ['data_type', 'time_step', 'time_step_items', 'tags']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(AddTSfromFileForm, self).__init__(*args, **kwargs)
        choices = Datafile.objects.filter(owner=user, current_state=10)
        datasets = RDataset.objects.filter(owner=user, current_state=10)
        self.fields['my_datasets'].queryset = datasets
        self.fields['selection'].choices=((0, _('Do nothing')), (1, _('Link time series to existing Dataset')), (2, _('Create new Dataset and link time series')))
        self.fields['selection'].help_text = 'If you want to organize extracted time series in a Dataset, please select an option above.'
        self.fields['datafile'].queryset = choices
        self.fields['datafile'].help_text = 'Please select a file containing time series data. Each line in the file must have comma-separated values (floats or integers). Example: "0.8386, -0.8372, 0.839, -0.84, 0.8389". File size should not exceed ' + filesizeformat(settings.MAX_FILE_PROCESSING_SIZE) + '.'
        self.fields['tags'].help_text = 'Values above will be applied to all time series, which are going to be created.'

    
class EditTSForm(forms.ModelForm):

    def clean_data(self):
        r = reg_csv()
        values = r.findall(self.cleaned_data["data"])
        cleaned_data = ''
        for value in values:
            try:
                a = float(value)
                cleaned_data += ', ' + str(a)
            except:
                raise forms.ValidationError(_('The data given is not a set of comma-separated float / integer values. Please check your input: %s') % value)
        if len(cleaned_data) > 0:
            cleaned_data = cleaned_data[2:]
        return cleaned_data

    class Meta:
        model = TimeSeries
        fields = ['caption', 'data', 'data_type', 'start_time', 
            'time_step', 'time_step_items', 'tags']

    def __init__(self, *args, **kwargs):
        super(EditTSForm, self).__init__(*args, **kwargs)
        self.fields['data'].help_text = 'Please insert comma-separated values (floats or integers) in the field. Example: "0.8386, -0.8372, 0.839, -0.84, 0.8389".'
        self.fields['data_type'].help_text = 'ANALOG - typically a voltage trace. SPIKES - typically a sequence of "0, 0, 0, 1, 0", representing spike times.'

class DeleteTSForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(DeleteTSForm, self).__init__(*args, **kwargs)
        values = TimeSeries.objects.filter(owner=user, current_state=10)
        # this should give nothing
        values = filter(lambda x: x.is_accessible(user), values)
        self.fields['serie_choices'] = forms.MultipleChoiceField(
            choices=[(c.id, c.title) for c in values], required=False,
            widget=widgets.CheckboxSelectMultiple)

class PrivacyEditForm(forms.ModelForm):
    
    class Meta:
        model = TimeSeries
        fields = ('safety_level', 'shared_with')
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PrivacyEditForm, self).__init__(*args, **kwargs)
        choices = User.objects.exclude(id__exact=user.id)
        self.fields['shared_with'] = MMCFClearField(queryset=choices)

