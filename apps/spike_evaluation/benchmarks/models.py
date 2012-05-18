##---IMPORTS

from django.db import models
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from tagging.fields import TagField

##---MODEL-REFS

#from spike_evaluation.evaluations.models import Evaluation
Evaluation = models.get_model('evaluations', 'evaluation')

##---MODELS

class Benchmark(models.Model):
    """Benchmark is a class representing a set of Benchmark data files,
    organized in Records. Each Record contains one Rawdata File with
    corresponding Groundtruth File (may be several due to different formats).
    Typically, a whole Benchmark belongs to one scientist.
    """

    ## choices

    BENCHMARK_STATES = [
        ('N', 'New/Non-active'),
        ('A', 'Active'),
        ('C', 'Closed'),
    ]

    ## fields

    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        'auth.User', related_name='benchmark owner', blank=True)
    state = models.CharField(
        max_length=1, default="N", choices=BENCHMARK_STATES)
    tags = TagField(_('keywords'))
    parameter_desc = models.CharField(
        _('parameter_desc'), max_length=255, default='Order')
    date_created = models.DateTimeField(
        _('date created'), default=datetime.now, editable=False)
    added_by = models.ForeignKey('auth.User', blank=True, editable=False)

    ## special methods

    def __unicode__(self):
        return self.name

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'b_detail', (), {'bid':self.pk}

    ## interface

    def is_active(self):
        return self.state == "A"

    def is_accessible(self, user):
        return (self.owner == user or self.is_active())

    def archive(self):
        self.state = "C"
        self.save()

    def resurrect(self):
        self.state = "N"
        self.save()

    def evaluations(self, pub_state=[1]):
        evals = Evaluation.objects.none()
        for r in self.record_set.all():
            evals |= r.evaluations(pub_state=pub_state)
        return evals

    def eval_count(self):
        return len(self.evaluations())


class Record(models.Model):
    """Record is a unique pair of Rawdata File  & Groundtruth File,
    representing a unit, against which users can make evaluations of their
    algorithms. Actually, there can be several raw data files in the record,
    however they should differ only with the format, not with their contents.
    """

    ## choices

    GT_IS_PUBLIC_STATES = [
        (0, 'PRIVATE'),
        (1, 'PUBLIC'),
    ]

    ## fields

    name = models.CharField(_('name'), blank=True, max_length=200)
    description = models.TextField(blank=True, null=True)
    benchmark = models.ForeignKey('Benchmark')
    parameter_value = models.FloatField(_('parameter_value'), default=0.0)
    gt_is_public = models.IntegerField(choices=GT_IS_PUBLIC_STATES, default=0)
    date_created = models.DateTimeField(
        _('date created'), default=datetime.now, editable=False)
    added_by = models.ForeignKey('auth.User', blank=True, editable=False)

    ## special methods

    def __unicode__(self):
        return self.name

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'b_record', (), {'rid':self.pk}

    ## interface

    def get_active_rfile(self):
        try:
            r = self.datafile_set.filter(filetype="R")[0]
        except IndexError:
            r = "#"
        return r

    def get_active_gfile(self):
        try:
            r = self.datafile_set.filter(filetype="G")[0]
        except IndexError:
            r = "#"
        return r

    def ever_validated(self):
        """This indicates whether a record had even been successfully
        validated, means, at present it still has a successfully validated
        pair of groundtruth - raw data files within different versions of
        related file pairs. That also means this record is available for
        users to download and perform evaluation against it."""

        rfile = self.get_active_rfile()
        gfile = self.get_active_gfile()
        for version in rfile.version_set.filter(validation_state="S"):
            if gfile.get_version(
                version=version.version).validation_state == "S":
                return True
        return False

    def last_validation_state(self):
        rv = self.get_active_rfile().get_last_version()
        gv = self.get_active_gfile().get_last_version()
        if rv.validation_state == "S" and gv.validation_state == "S":
            result = "S" # success
        elif rv.validation_state == "F" or gv.validation_state == "F":
            result = "F" # failure
        else:
            result = "I" # in progress or broken
        return result

    def last_validation_log(self):
        rv = self.get_active_rfile().get_last_version()
        gv = self.get_active_gfile().get_last_version()
        return '\n'.join([
            'Rawdata File: %s' % rv.get_validation_state_display(),
            'Task ID: %s' % rv.validation_task_id,
            rv.validation_log,
            '',
            'Groundtruth File: %s' % gv.get_validation_state_display(),
            'Task ID: %s' % gv.validation_task_id,
            gv.validation_log])

    def evaluations(self, pub_state=[1]):
        evals = Evaluation.objects.none()
        for f in self.datafile_set.all():
            evals |= f.evaluations(pub_state=pub_state)
        return evals

    def eval_count(self):
        return len(self.evaluations())

##---MAIN

if __name__ == '__main__':
    pass
