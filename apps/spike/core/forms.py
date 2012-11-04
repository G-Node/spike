##---IMPORTS

from captcha.fields import CaptchaField
from django import forms
from django.db import models

##---MODEL-REFS

Benchmark = models.get_model('spike', 'benchmark')
Trial = models.get_model('spike', 'trial')
Datafile = models.get_model('spike', 'datafile')
Batch = models.get_model('spike', 'batch')
Evaluation = models.get_model('spike', 'evaluation')
Algorithm = models.get_model('spike', 'algorithm')

##---FORMS

class BenchmarkForm(forms.ModelForm):
    class Meta:
        model = Benchmark
        exclude = ('created', 'modified', 'status_changed', 'metrics')

    ## constructor

    def __init__(self, *args, **kwargs):
        super(BenchmarkForm, self).__init__(*args, **kwargs)
        if self.instance.id is None:
            self.fields.pop('status')
            self.fields.pop('owner')

    ## form interface

    def save(self, *args, **kwargs):
        if self.instance.id is None:
            us = kwargs.pop('user', None)
            if us is not None:
                self.instance.owner = us
        return super(BenchmarkForm, self).save(*args, **kwargs)


class TrialForm(forms.ModelForm):
    class Meta:
        model = Trial
        exclude = ('created', 'modified', 'valid_rd_log', 'valid_gt_log')


    ## fields

    rd_upload = forms.FileField(label='Rawdata File', required=False)
    gt_upload = forms.FileField(label='Groundtruth File', required=False)

    ## constructor

    def __init__(self, *args, **kwargs):
        pv_label = kwargs.pop('pv_label', None)
        super(TrialForm, self).__init__(*args, **kwargs)
        if self.instance.id is None:
            self.fields.pop('benchmark')
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
            if 'rd_upload' not in self.changed_data:
                return
            self.instance.benchmark = kwargs.pop('benchmark', None)
        tr = super(TrialForm, self).save(*args, **kwargs)

        # handling rd_file upload
        if 'rd_upload' in self.changed_data:
            if tr.rd_file:
                tr.rd_file.delete()
            rd_file = Datafile(
                name=self.cleaned_data['rd_upload'].name,
                file=self.cleaned_data['rd_upload'],
                file_type='rd_file',
                content_object=tr)
            rd_file.save()

        # handling gt_file upload
        if 'gt_upload' in self.changed_data:
            if tr.gt_file:
                tr.gt_file.delete()
            gt_file = Datafile(
                name=self.cleaned_data['gt_upload'].name,
                file=self.cleaned_data['gt_upload'],
                file_type='st_file',
                content_object=tr)
            gt_file.save()

        # validate
        tr.validate()

        # return
        return tr


class BatchEditForm(forms.ModelForm):
    class Meta:
        model = Batch
        exclude = ('status', 'status_changed', 'benchmark')


class BatchSubmitForm(forms.ModelForm):
    class Meta:
        model = Batch
        exclude = ('owner', 'status', 'status_changed', 'benchmark')

    ## fields

    captcha = CaptchaField()

    ## constructor

    def __init__(self, *args, **kwargs):
        self.benchmark = kwargs.pop('benchmark')
        super(BatchSubmitForm, self).__init__(*args, **kwargs)
        self.sub_ids = []
        for tr in self.benchmark.trial_set_valid():
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
        self.instance.status = Batch.STATUS.private
        bt = super(BatchSubmitForm, self).save(*args, **kwargs)

        # evaluations
        for sub_id in self.sub_ids:
            if not self.cleaned_data[sub_id]:
                continue

            # evaluation
            pk = int(sub_id.split('-')[-1])
            tr = Trial.objects.get(id=pk)
            ev = Evaluation(batch=bt, trial=tr)
            ev.save()

            # datafile
            ev_file = Datafile(
                name=self.cleaned_data[sub_id].name,
                file=self.cleaned_data[sub_id],
                file_type='st_file',
                content_object=ev)
            ev_file.save()
            ev.validate()

            # trigger evaluation
            ev.run()
        return bt


class AlgorithmForm(forms.ModelForm):
    class Meta:
        model = Algorithm

    ## constructor

    def __init__(self, *args, **kwargs):
        super(AlgorithmForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if user is not None:
            self.instance.owner = user
        return super(AlgorithmForm, self).save(*args, **kwargs)


class AppendixForm(forms.ModelForm):
    class Meta:
        model = Datafile
        fields = ('name', 'file')

    ## constructor

    def __init__(self, *args, **kwargs):
        super(AppendixForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # init and checks
        obj = kwargs.pop('obj')
        user = kwargs.pop('user', obj.owner)

        # build instance
        self.instance.file_type = 40
        self.instance.added_by = user
        self.instance.content_object = obj
        return super(AppendixForm, self).save(*args, **kwargs)

if __name__ == '__main__':
    pass
