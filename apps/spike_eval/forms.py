##---IMPORTS

from captcha.fields import ReCaptchaField as CaptchaField
from datetime import datetime
from django import forms
from .benchmark.models import Benchmark, Trial
from .datafile.models import Datafile
from .evaluation.models import Algorithm, Evaluation, EvaluationBatch
from .tasks import (
    start_evaluation, validate_groundtruth_file, validate_rawdata_file)

##---FORMS

class BenchmarkForm(forms.ModelForm):
    class Meta:
        model = Benchmark
        exclude = ('owner', 'date_created', 'added_by')

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
            benchmark = kwargs.pop('benchmark')
            user = kwargs.pop('user')
            self.instance.benchmark = benchmark
            self.instance.added_by = user
            self.instance.date_create = datetime.now()
            if 'rd_upload' not in self.changed_data:
                # XXX: check before save!!
                # TODO: better handling??
                raise forms.ValidationError
        else:
            user = self.instance.added_by
        t = super(TrialForm, self).save(*args, **kwargs)

        # handling rd_file upload
        if 'rd_upload' in self.changed_data:
            if t.rd_file:
                t.rd_file.delete()
            rd_file = Datafile(
                name=self.cleaned_data['rd_upload'].name,
                file=self.cleaned_data['rd_upload'],
                file_type=10,
                added_by=user,
                content_object=t)
            rd_file.save()
            rd_file.task_id = validate_rawdata_file(rd_file.id)

        # handling gt_file upload
        if 'gt_upload' in self.changed_data:
            if t.gt_file:
                t.gt_file.delete()
            gt_file = Datafile(
                name=self.cleaned_data['gt_upload'].name,
                file=self.cleaned_data['gt_upload'],
                file_type=20,
                added_by=user,
                content_object=t)
            gt_file.save()
            gt_file.task_id = validate_groundtruth_file(gt_file.id)

        # return
        return t


class EvalBatchEditForm(forms.ModelForm):
    class Meta:
        model = EvaluationBatch
        exclude = ('added_by', 'date_created', 'access', 'benchmark')


class EvaluationSubmitForm(forms.ModelForm):
    class Meta:
        model = EvaluationBatch
        exclude = ('added_by', 'date_created', 'access', 'benchmark')

    ## fields

    captcha = CaptchaField()

    ## constructor

    def __init__(self, *args, **kwargs):
        self.benchmark = kwargs.pop('benchmark')
        super(EvaluationSubmitForm, self).__init__(*args, **kwargs)
        self.sub_ids = []
        for t in self.benchmark.trial_set.all():
            self.sub_ids.append('sub-t-%s' % t.id)
            self.fields['sub-t-%s' % t.id] = forms.FileField(
                label='Upload Trial: %s' % t.name,
                required=False)

    def save(self, *args, **kwargs):
        # init and checks
        user = kwargs.pop('user')

        # build instance
        self.instance.added_by = user
        self.instance.benchmark = self.benchmark
        self.instance.access = 10
        eb = super(EvaluationSubmitForm, self).save(*args, **kwargs)

        # evaluations
        for sub_id in self.sub_ids:
            if not self.cleaned_data[sub_id]:
                continue

            # evaluation
            tid = int(sub_id.split('-')[-1])
            trial = Trial.objects.get(id=tid)
            e = Evaluation(
                added_by=user,
                evaluation_batch=eb,
                trial=trial)
            e.save()

            # datafile
            ev_file = Datafile(
                name=self.cleaned_data[sub_id].name,
                file=self.cleaned_data[sub_id],
                file_type=30,
                added_by=user,
                content_object=e)
            ev_file.save()

            # trigger evaluation
            e.task_id = start_evaluation(e.id)
            e.save()
        return eb

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
            self.instance.added_by = kwargs.pop('user')
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
        user = kwargs.pop('user', obj.added_by)

        # build instance
        self.instance.file_type = 40
        self.instance.added_by = user
        self.instance.content_object = obj
        return super(SupplementaryForm, self).save(*args, **kwargs)

if __name__ == '__main__':
    pass
