##---IMPORTS

from datetime import datetime

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from .benchmark.models import Benchmark, Trial
from .datafile.models import Datafile
from .evaluation.models import Evaluation
from .tasks import (
    start_eval, validate_groundtruth_file, validate_rawdata_file)

##---CONSTANTS

USE_CELERY = getattr(settings, 'USE_CELERY', False)
TrialType = ContentType.objects.get_for_model(Trial)

##---CLASSES

class BenchmarkForm(forms.ModelForm):
    class Meta:
        model = Benchmark
        exclude = ('owner', 'date_created', 'added_by')

    ## fields

    action = forms.CharField(widget=forms.HiddenInput, initial='b_edit',
                             required=False)

    ## constructor

    def __init__(self, *args, **kwargs):
        super(BenchmarkForm, self).__init__(*args, **kwargs)
        #if 'instance' not in kwargs:
        if self.instance.id is None:
            self.initial['action'] = 'b_create'
            self.fields.pop('state')
        else:
            self.initial['action'] = 'b_edit'

    ## form interface

    def save(self, *args, **kwargs):
        if self.instance.id is None:
            user = kwargs.pop('user')
            self.instance.owner = user
            self.instance.added_by = user
        return super(BenchmarkForm, self).save(*args, **kwargs)


class TrialForm(forms.ModelForm):
    class Meta:
        model = Trial
        exclude = ('benchmark', 'date_created', 'added_by')

    ## fields

    rd_file = forms.FileField(label='Rawdata File')
    gt_file = forms.FileField(label='Groundtruth File', required=False)
    action = forms.CharField(widget=forms.HiddenInput, initial='t_edit')

    ## constructor

    def __init__(self, *args, **kwargs):
        pv_label = kwargs.pop('pv_label', None)
        super(TrialForm, self).__init__(*args, **kwargs)
        #if 'instance' not in kwargs:
        if self.instance.id is None:
            self.initial['action'] = 't_create'
        else:
            self.initial['action'] = 't_edit'
        if pv_label is not None:
            self.fields['parameter'].label = pv_label

    ## form interface

    def save(self, *args, **kwargs):
        if self.instance.id is None:
            try:
                # init and checks
                benchmark = kwargs.pop('benchmark')
                user = kwargs.pop('user')

                # trial
                self.instance.benchmark = benchmark
                self.instance.added_by = user
                self.instance.date_create = datetime.now()
                t = super(TrialForm, self).save(*args, **kwargs)

                # creating rd_file
                rd_file = Datafile(
                    name=self.cleaned_data['rd_file'].name,
                    file=self.cleaned_data['rd_file'],
                    filetype=10,
                    added_by=user,
                    content_object=t)
                rd_file.save()
                if USE_CELERY:
                    rval = validate_rawdata_file.delay(rd_file.id)
                    rd_file.task_id = str(rval.task_id)
                else:
                    rval = validate_rawdata_file(rd_file.id)
                    rd_file.task_id = '00'

                # creating gt_file
                if self.cleaned_data['gt_file']:
                    gt_file = Datafile(
                        name=self.cleaned_data['gt_file'].name,
                        file=self.cleaned_data['gt_file'],
                        filetype=20,
                        added_by=user,
                        content_object=t)
                    gt_file.save()
                    if USE_CELERY:
                        rval = validate_groundtruth_file.delay(gt_file.id)
                        gt_file.task_id = str(rval.task_id)
                    else:
                        rval = validate_groundtruth_file(gt_file.id)
                        gt_file.task_id = '00'

            except Exception, ex:
                print 'shit happened during save'
                print str(ex)
                raise
            else:
                return t
        else:
            return super(TrialForm, self).save(*args, **kwargs)


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ('algorithm',)

    ## fields

    ev_file = forms.FileField(label='Evaluation File')

    ## constructor

    def __init__(self, *args, **kwargs):
        super(EvaluationForm, self).__init__(*args, **kwargs)
        self.tid = None
        self.trial = None
        if self.prefix is not None:
            self.tid = int(self.prefix.split('-')[1])
            try:
                self.trial = Trial.objects.get(id=self.tid)
            except:
                pass

    ## for interface

    def clean(self):
        cleaned_data = self.cleaned_data

        if self._errors and 'file' in self._errors:
            self._errors.clear()
            raise forms.ValidationError('nothing submitted')
        else:
            return cleaned_data

    def save(self, *args, **kwargs):
        try:
            # init and checks
            user = kwargs.pop('user')
            if self.tid is None:
                self.tid = int(kwargs.pop('tid'))
            self.trial = Trial.objects.get(id=self.tid)

            # build instance
            self.instance.owner = user
            self.instance.added_by = user
            self.instance.trial = self.trial
            self.instance.task_state = 10
            self.instance.access = 10
            e = super(EvaluationForm, self).save(*args, **kwargs)
            e.save()

            # datafile
            ev_file = Datafile(
                name=self.cleaned_data['ev_file'].name,
                file=self.cleaned_data['ev_file'],
                filetype=30,
                added_by=user,
                content_object=e)
            ev_file.save()

            # trigger evaluation
            if USE_CELERY:
                rval = start_eval.delay(e.id)
                e.task_id = str(rval.task_id)
            else:
                start_eval(e.id)
                e.task_id = '00'
            e.save()

        except Exception, ex:
            print 'shit happened during save'
            print str(ex)
            raise
        else:
            return e


class SupplementaryForm(forms.ModelForm):
    class Meta:
        model = Datafile
        fields = ('name', 'file')

    ## fields

    action = forms.CharField(widget=forms.HiddenInput, initial='s_create')

    ## constructor

    def __init__(self, *args, **kwargs):
        super(SupplementaryForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # init and checks
        benchmark = kwargs.pop('benchmark')
        user = kwargs.pop('user')

        # build instance
        self.instance.filetype = 40
        self.instance.added_by = user
        self.instance.content_object = benchmark
        dfile = super(SupplementaryForm, self).save(*args, **kwargs)
        dfile.save()
        return dfile

if __name__ == '__main__':
    pass
