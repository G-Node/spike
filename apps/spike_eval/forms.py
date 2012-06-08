##---IMPORTS

from datetime import datetime
from django import forms
from .benchmark.models import Benchmark, Trial
from .datafile.models import Datafile
from .evaluation.models import Algorithm, Evaluation, EvaluationBatch
from .tasks import (
    start_eval, validate_groundtruth_file, validate_rawdata_file)

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

    rd_file = forms.FileField(label='Rawdata File')
    gt_file = forms.FileField(label='Groundtruth File', required=False)
    action = forms.CharField(widget=forms.HiddenInput)

    ## constructor

    def __init__(self, *args, **kwargs):
        pv_label = kwargs.pop('pv_label', None)
        super(TrialForm, self).__init__(*args, **kwargs)
        #if 'instance' not in kwargs:
        if self.instance.id is None:
            self.initial['action'] = 't_create'
        else:
            self.initial['action'] = 't_edit'
            self.initial['rd_file'] = self.instance.rd_file
            if self.instance.gt_file:
                self.initial['gt_file'] = self.instance.gt_file
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
                if self.cleaned_data['rd_file']:
                    rd_file = Datafile(
                        name=self.cleaned_data['rd_file'].name,
                        file=self.cleaned_data['rd_file'],
                        filetype=10,
                        added_by=user,
                        content_object=t)
                    rd_file.save()
                    rd_file.task_id = validate_rawdata_file(rd_file.id)

                # creating gt_file
                if self.cleaned_data['gt_file']:
                    gt_file = Datafile(
                        name=self.cleaned_data['gt_file'].name,
                        file=self.cleaned_data['gt_file'],
                        filetype=20,
                        added_by=user,
                        content_object=t)
                    gt_file.save()
                    gt_file.task_id = validate_groundtruth_file(gt_file.id)

            except Exception, ex:
                print 'shit happened during save'
                print str(ex)
                raise
            else:
                return t
        else:
            return super(TrialForm, self).save(*args, **kwargs)


class EvaluationSubmitForm(forms.ModelForm):
    class Meta:
        model = EvaluationBatch
        exclude = ('added_by', 'date_created', 'access', 'benchmark')

    ## constructor

    def __init__(self, *args, **kwargs):
        self.benchmark = kwargs.pop('benchmark')
        super(EvaluationSubmitForm, self).__init__(*args, **kwargs)
        self.sub_ids = []
        self.sub_ommited = []
        for t in self.benchmark.trial_set.all():
            self.sub_ids.append('sub-t-%s' % t.id)
            self.fields['sub-t-%s' % t.id] = forms.FileField(
                label='Upload Trial: %s' % t.name)

    ## form interface

    def clean(self):
        cleaned_data = self.cleaned_data

        if self._errors:
            print self._errors
            for sub_id in self.sub_ids:
                if sub_id in self._errors:
                    self.sub_ommited.append(self._errors.pop(sub_id))
        return cleaned_data

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
            if sub_id in self.sub_ommited:
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
                filetype=30,
                added_by=user,
                content_object=e)
            ev_file.save()

            # trigger evaluation
            e.task_id = start_eval(e.id)
            e.save()
        return eb


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ()

    ## fields

    ev_file = forms.FileField(label='Evaluation File')

    ## constructor

    def __init__(self, *args, **kwargs):
        super(EvaluationForm, self).__init__(*args, **kwargs)
        self.tid = None
        self.trial = None
        if self.prefix is not None:
            self.tid = int(self.prefix.split('-')[1])
            self.trial = Trial.objects.get(id=self.tid)

    ## form interface

    def clean(self):
        cleaned_data = self.cleaned_data

        if self._errors and 'file' in self._errors:
            self._errors.clear()
            raise forms.ValidationError('nothing submitted')
        else:
            return cleaned_data

    def save(self, *args, **kwargs):
        # init and checks
        batch = kwargs.pop('batch')
        user = kwargs.pop('user')
        if self.tid is None:
            self.tid = int(kwargs.pop('tid'))
        self.trial = Trial.objects.get(id=self.tid)

        # build instance
        self.instance.added_by = user
        self.instance.trial = self.trial
        self.instance.task_state = 10
        self.instance.evaluation_batch = batch
        e = super(EvaluationForm, self).save(*args, **kwargs)

        # datafile
        ev_file = Datafile(
            name=self.cleaned_data['ev_file'].name,
            file=self.cleaned_data['ev_file'],
            filetype=30,
            added_by=user,
            content_object=e)
        ev_file.save()

        # trigger evaluation
        e.task_id = start_eval(e.id)
        e.save()
        return e


class AlgorithmForm(forms.ModelForm):
    class Meta:
        model = Algorithm


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
        user = kwargs.pop('user')

        # build instance
        self.instance.filetype = 40
        self.instance.added_by = user
        self.instance.content_object = obj
        dfile = super(SupplementaryForm, self).save(*args, **kwargs)
        dfile.save()
        return dfile

if __name__ == '__main__':
    pass
