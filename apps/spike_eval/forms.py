##---IMPORTS

from captcha.fields import CaptchaField
from datetime import datetime
from django import forms
from .models import Benchmark, Trial
from .models import Datafile
from .models import Algorithm, Evaluation, Batch
from .tasks import start_evaluation, validate_groundtruth_file, validate_rawdata_file
from .util import ACCESS_CHOICES

##---FORMS

class BenchmarkForm(forms.ModelForm):
    class Meta:
        model = Benchmark
        exclude = ('owner', 'created', 'modified', 'status_changed', 'metrics')

    ## constructor

    def __init__(self, *args, **kwargs):
        super(BenchmarkForm, self).__init__(*args, **kwargs)
        if self.instance.id is None:
            self.initial['action'] = 'b_create'
            self.fields.pop('status')
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
        exclude = ('benchmark', 'created', 'modified')

    ## fields

    rd_upload = forms.FileField(label='Rawdata File', required=False)
    gt_upload = forms.FileField(label='Groundtruth File', required=False)

    ## constructor

    def __init__(self, *args, **kwargs):
        pv_label = kwargs.pop('pv_label', None)
        super(TrialForm, self).__init__(*args, **kwargs)
        if self.instance.rd_file:
            self.initial['rd_upload'] = self.instance.rd_file.file
        if self.instance.gt_file:
            self.initial['gt_upload'] = self.instance.gt_file.file
        if pv_label is not None:
            self.fields['parameter'].label = pv_label

    ## form interface

    def save(self, *args, **kwargs):
        # init and checks
        if not self.changed_data:
            return
        if self.instance.id is None:
            bm = kwargs.pop('benchmark')
            us = kwargs.pop('user')
            self.instance.benchmark = bm
            if 'rd_upload' not in self.changed_data:
                raise forms.ValidationError
        else:
            us = self.instance.benchmark.owner
        tr = super(TrialForm, self).save(*args, **kwargs)

        # handling rd_file upload
        if 'rd_upload' in self.changed_data:
            if tr.rd_file:
                tr.rd_file.delete()
            rd_file = Datafile(
                name=self.cleaned_data['rd_upload'].name,
                file=self.cleaned_data['rd_upload'],
                file_type=10,
                content_object=tr)
            rd_file.save()
            rd_file.task_id = validate_rawdata_file(rd_file.id)

        # handling gt_file upload
        if 'gt_upload' in self.changed_data:
            if tr.gt_file:
                tr.gt_file.delete()
            gt_file = Datafile(
                name=self.cleaned_data['gt_upload'].name,
                file=self.cleaned_data['gt_upload'],
                file_type=20,
                content_object=tr)
            gt_file.save()
            gt_file.task_id = validate_groundtruth_file(gt_file.id)

        # return
        return tr


class BatchEditForm(forms.ModelForm):
    class Meta:
        model = Batch
        exclude = ('owner', 'status', 'status_changed', 'benchmark')


class EvaluationSubmitForm(forms.ModelForm):
    class Meta:
        model = Batch
        exclude = ('owner', 'status', 'status_changed', 'benchmark')

    ## fields

    captcha = CaptchaField()

    ## constructor

    def __init__(self, *args, **kwargs):
        self.benchmark = kwargs.pop('benchmark')
        super(EvaluationSubmitForm, self).__init__(*args, **kwargs)
        self.sub_ids = []
        for tr in self.benchmark.trial_set.all():
            self.sub_ids.append('sub-tr-%s' % tr.id)
            self.fields['sub-tr-%s' % tr.id] = forms.FileField(
                label='Upload Trial: %s' % tr.name,
                required=False)

    def save(self, *args, **kwargs):
        # init and checks
        user = kwargs.pop('user')

        # build instance
        self.instance.owner = user
        self.instance.benchmark = self.benchmark
        self.instance.status = ACCESS_CHOICES.private
        bt = super(EvaluationSubmitForm, self).save(*args, **kwargs)

        # evaluations
        for sub_id in self.sub_ids:
            if not self.cleaned_data[sub_id]:
                continue

            # evaluation
            tid = int(sub_id.split('-')[-1])
            trial = Trial.objects.get(id=tid)
            ev = Evaluation(
                batch=bt,
                trial=trial)
            ev.save()

            # datafile
            ev_file = Datafile(
                name=self.cleaned_data[sub_id].name,
                file=self.cleaned_data[sub_id],
                file_type=30,
                content_object=ev)
            ev_file.save()

            # trigger evaluation
            ev.task_id = start_evaluation(ev.id)
            ev.save()
        return bt

#
#class EvaluationForm(forms.ModelForm):
#    class Meta:
#        model = Evaluation
#        fields = ()
#
#    ## fields
#
#    ev_file = forms.FileField(label='Evaluation File')
#
#    ## constructor
#
#    def __init__(self, *args, **kwargs):
#        super(EvaluationForm, self).__init__(*args, **kwargs)
#        self.tid = None
#        self.trial = None
#        if self.prefix is not None:
#            self.tid = int(self.prefix.split('-')[1])
#            self.trial = Trial.objects.get(id=self.tid)
#
#    ## form interface
#
#    def clean(self):
#        cleaned_data = self.cleaned_data
#
#        if self._errors and 'file' in self._errors:
#            self._errors.clear()
#            raise forms.ValidationError('nothing submitted')
#        else:
#            return cleaned_data
#
#    def save(self, *args, **kwargs):
#        # init and checks
#        batch = kwargs.pop('batch')
#        user = kwargs.pop('user')
#        if self.tid is None:
#            self.tid = int(kwargs.pop('tid'))
#        self.trial = Trial.objects.get(id=self.tid)
#
#        # build instance
#        self.instance.added_by = user
#        self.instance.trial = self.trial
#        self.instance.task_state = 10
#        self.instance.evaluation_batch = batch
#        e = super(EvaluationForm, self).save(*args, **kwargs)
#
#        # datafile
#        ev_file = Datafile(
#            name=self.cleaned_data['ev_file'].name,
#            file=self.cleaned_data['ev_file'],
#            file_type=30,
#            added_by=user,
#            content_object=e)
#        ev_file.save()
#
#        # trigger evaluation
#        e.task_id = start_eval(e.id)
#        e.save()
#        return e


class AlgorithmForm(forms.ModelForm):
    class Meta:
        model = Algorithm

    ## constructor

    def __init__(self, *args, **kwargs):
        super(AlgorithmForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if 'user' in kwargs:
            self.instance.owner = kwargs.pop('user')
        return super(AlgorithmForm, self).save(*args, **kwargs)


class SupplementaryForm(forms.ModelForm):
    class Meta:
        model = Datafile
        fields = ('name', 'file')

    ## constructor

    def __init__(self, *args, **kwargs):
        super(SupplementaryForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # init and checks
        obj = kwargs.pop('obj')
        user = kwargs.pop('user', obj.owner)

        # build instance
        self.instance.file_type = 40
        self.instance.added_by = user
        self.instance.content_object = obj
        return super(SupplementaryForm, self).save(*args, **kwargs)

if __name__ == '__main__':
    pass
