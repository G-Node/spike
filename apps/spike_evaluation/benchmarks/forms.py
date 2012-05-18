##---HEADER


##---IMPORTS

from os.path import basename
from datetime import datetime

from django import forms

from benchmarks.models import Benchmark, Record
from dfiles.models import Datafile, Version
from evaluations.models import Evaluation
from spike_evaluation.tasks import evaluate, validate_record

##---FUNCTIONS

def validation_run(r, gv, rv):
    # start a task to validate the record
    extracted = validate_record.delay(r.id)
    task_id = str(extracted.task_id)
    gv.validation_task_id = task_id
    rv.validation_task_id = task_id
    gv.save()
    rv.save()


def evaluation_run(e):
    # inits and checks
    r = e.record()
    rdv = r.get_active_rfile().get_last_version()
    path_rd = rdv.raw_file.path
    path_ev = e.user_file.path
    gtv = r.get_active_gfile().get_last_version()
    path_gt = gtv.raw_file.path

    # start task
    evaluated = evaluate.delay(path_rd, path_ev, path_gt, e.id)
    task_id = str(evaluated.task_id)
    e.evaluation_task_id = task_id
    e.save()

##---CLASSES

class BenchmarkForm(forms.ModelForm):
    class Meta:
        model = Benchmark
        exclude = ('owner', 'date_created', 'added_by')

    ## fields

    parameter_desc = forms.CharField(label='Parameter Description (Unit)',
                                     max_length=255)
    action = forms.CharField(widget=forms.HiddenInput, initial='b_edit',
                             required=False)

    ## constructor

    def __init__(self, *args, **kwargs):
        super(BenchmarkForm, self).__init__(*args, **kwargs)
        #if 'instance' not in kwargs:
        if self.instance.id is None:
            self.initial['action'] = 'b_create'
        else:
            self.initial['action'] = 'b_edit'

    ## form interface

    def save(self, *args, **kwargs):
        #if self.cleaned_data['action'] == 'b_create':
        if self.instance.id is None:
            user = kwargs.pop('user')
            self.instance.owner = user
            self.instance.added_by = user
            self.instance.state = 'N'
        return super(BenchmarkForm, self).save(*args, **kwargs)


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        exclude = ('benchmark', 'date_created', 'added_by')

    ## fields

    r_file = forms.FileField(label="Rawdata File")
    g_file = forms.FileField(label="Groundtruth File")
    action = forms.CharField(widget=forms.HiddenInput, initial='r_edit')

    ## constructor

    def __init__(self, *args, **kwargs):
        pv_label = kwargs.pop('pv_label', None)
        super(RecordForm, self).__init__(*args, **kwargs)
        #if 'instance' not in kwargs:
        if self.instance.id is None:
            self.initial['action'] = 'r_create'
        else:
            self.initial['action'] = 'r_edit'
            self.fields.pop('r_file')
            self.fields.pop('g_file')
        if pv_label is not None:
            self.fields['parameter_value'].label = pv_label

    ## form interface

    def save(self, *args, **kwargs):
        #if self.cleaned_data['action'] == 'r_create':
        if self.instance.id is None:
            try:
                # inits and checks
                benchmark = kwargs.pop('benchmark')
                user = kwargs.pop('user')
                rf = rv = gf = gv = None

                # record
                self.instance.benchmark = benchmark
                self.instance.added_by = user
                self.instance.date_create = datetime.now()
                r = super(RecordForm, self).save(*args, **kwargs)
                r.save()

                # creating datafiles
                rf = Datafile(filetype='R', record=r, added_by=user)
                rf.save()
                gf = Datafile(filetype='G', record=r, added_by=user)
                gf.save()

                # creating first versions
                rv = Version(title=self.cleaned_data['r_file'].name,
                             version=1,
                             datafile=rf,
                             raw_file=self.cleaned_data['r_file'],
                             added_by=user)
                rv.save()
                gv = Version(title=self.cleaned_data['g_file'].name,
                             version=1,
                             datafile=gf,
                             raw_file=self.cleaned_data['g_file'],
                             added_by=user)
                gv.save()

                # validation
                validation_run(r, gv, rv)
                r.save()

            except Exception, ex:
                print 'shit happened during save'
                print str(ex)
                raise
            else:
                return r
        else:
            return super(RecordForm, self).save(*args, **kwargs)


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ('algorithm', 'description', 'user_file')

    ## fields

    description = forms.CharField()

    ## constructor

    def __init__(self, *args, **kwargs):
        super(EvaluationForm, self).__init__(*args, **kwargs)
        self.rid = None
        self.record = None
        if self.prefix is not None:
            self.rid = int(self.prefix.split('-')[1])
            try:
                self.record = Record.objects.get(id=self.rid)
            except:
                pass

    ## for interface

    def clean(self):
        cleaned_data = self.cleaned_data

        if self._errors and 'user_file' in self._errors:
            self._errors.clear()
            raise forms.ValidationError('nothing submitted')
        else:
            return cleaned_data

    def save(self, *args, **kwargs):
        try:
            # inits and checks
            user = kwargs.pop('user')
            if self.rid is None:
                self.rid = int(kwargs.pop('rid'))
            r = Record.objects.get(id=self.rid)

            # build instance
            self.instance.owner = user
            self.instance.added_by = user
            self.instance.original_file =\
            r.get_active_gfile().get_last_version()
            self.instance.processing_state = 10
            self.instance.publication_state = 0
            e = super(EvaluationForm, self).save(*args, **kwargs)
            e.save()

            # trigger evaluation
            evaluation_run(e)
            e.save()

        except Exception, ex:
            print 'shit happened during save'
            print str(ex)
            raise
        else:
            return e


class VersionForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = ('raw_file',)

    ## fields

    action = forms.CharField(widget=forms.HiddenInput, initial='v_create')
    rid = forms.CharField(widget=forms.HiddenInput)

    ## constructor

    def __init__(self, *args, **kwargs):
        super(VersionForm, self).__init__(*args, **kwargs)
        if self.instance.id is not None:
            self.initial.pop('raw_file')

    ## form interface

    def save(self, *args, **kwargs):
        if self.instance.id is not None:
            self.instance.id = None

        try:
            # inits and checks
            d = self.instance.datafile
            r = d.record
            rv = gv = None

            # build version
            self.instance.title = basename(self.cleaned_data['raw_file'].name)
            self.instance.version = d.get_next_version_index()
            self.instance.date_created = datetime.now()
            v = super(VersionForm, self).save(*args, **kwargs)
            v.save()

            # get record stuff
            if d.filetype == 'G':
                rv = r.get_active_rfile()
                gv = v
            elif d.filetype == 'R':
                rv = v
                gv = r.get_active_gfile()

            # validation
            validation_run(r, gv, rv)

        except Exception, ex:
            print 'shit happened during save'
            print str(ex)
            raise
        else:
            return v

if __name__ == '__main__':
    pass
