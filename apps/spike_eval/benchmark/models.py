##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager

from ..models import CommonInfo
from ..util import ACCESS_CHOICES

##---MODEL-REFS

Datafile = models.get_model('datafile', 'datafile')
Evaluation = models.get_model('evaluation', 'evaluation')

##---CONSTANTS

TAG_NAMESPACE = 'Benchmark Tags'

##---MODELS

class Benchmark(CommonInfo):
    """container for trials

    A Benchmark represents a set of Trials that belong together, and usually
    originate from the same source.
    """

    ## choices

    STATES_CHOICES = [
        (10, 'New'),
        (20, 'Active'),
        (30, 'Closed'),
    ]

    ## fields

    name = models.CharField(
        max_length=255)
    description = models.TextField(
        blank=True,
        null=True)
    state = models.IntegerField(
        choices=STATES_CHOICES,
        default=10)
    parameter = models.CharField(
        max_length=255,
        default='Order')

    owner = models.ForeignKey(
        'auth.User',
        related_name='benchmark owner',
        blank=True)

    tags = TaggableManager(_(TAG_NAMESPACE))

    ## special methods

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.__str__())

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'b_detail', (), {'bid':self.pk}

    def delete(self, *args, **kwargs):
        for t in self.trial_set:
            t.delete()
        for d in self.datafile_set:
            d.delete()
        super(Benchmark, self).delete(*args, **kwargs)

    ## interface

    @property
    def datafile_set(self):
        return Datafile.objects.for_obj(self)

    @property
    def sp_files(self):
        try:
            return self.datafile_set.filter(filetype=40)
        except IndexError:
            return []

    def is_active(self):
        return self.state == 20

    def is_accessible(self, user):
        return self.owner == user or self.is_active()

    def archive(self):
        self.state = 30
        self.save()

    def resurrect(self):
        self.state = 20
        self.save()

    def evaluations(self, state=10):
        e_set = Evaluation.objects.none()
        for t in self.trial_set.all():
            e_set |= t.evaluations(state=state)
        return e_set

    def eval_count(self):
        return len(self.evaluations())


class Trial(CommonInfo):
    """represents an experimental trial

    A Trial consists of raw data and, (if applicable) the corresponding ground
    truth for that raw data. Each is stored in separate files. Raw data is
    generally accessible to the user, while the ground truth is generally
    inaccessible, but can be flagged as available to the user.


    Raw data is stored in hdf5 format, ground truth is stored in gdf format.
    """

    ## fields

    name = models.CharField(
        max_length=255)
    description = models.TextField(
        blank=True,
        null=True)
    parameter = models.FloatField(
        default=0.0)
    gt_access = models.IntegerField(
        choices=ACCESS_CHOICES,
        default=10)

    benchmark = models.ForeignKey(
        'Benchmark')

    tags = TaggableManager(_(TAG_NAMESPACE))

    ## special methods

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.name)

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'b_trial', (), {'tid':self.pk}

    def delete(self, *args, **kwargs):
        for d in self.datafile_set:
            d.delete()
        super(Trial, self).delete(*args, **kwargs)

    ## interface

    @property
    def datafile_set(self):
        return Datafile.objects.for_obj(self)

    @property
    def rd_file(self):
        try:
            return self.datafile_set.filter(filetype=10)[0]
        except IndexError:
            return None

    @property
    def gt_file(self):
        try:
            return self.datafile_set.filter(filetype=20)[0]
        except IndexError:
            return None

    def is_validated(self):
        """This indicates whether a trial had even been successfully
        validated, means, at present it still has a successfully validated
        pair of groundtruth - raw data files within different versions of
        related file pairs. That also means this trial is available for
        users to download and perform evaluation against it."""

        rd_good = self.rd_file.task_state == 20
        gt_good = None
        if self.gt_file:
            gt_good = self.gt_file.task_state == 20
        return rd_good and (gt_good or True)

    def validation_log(self):
        rval = [
            'Rawdata File: %s' % self.rd_file.get_task_state_display(),
            'Task ID: %s' % self.rd_file.task_id,
            self.rd_file.task_log, '']
        if self.gt_file is None:
            rval.extend('Groundtruth File: does not exist')
        else:
            rval.extend([
                'Groundtruth File: %s' % self.gt_file.get_task_state_display(),
                'Task ID: %s' % self.gt_file.task_id,
                self.gt_file.task_log])
        return '\n'.join(rval)

    def evaluations(self, state=10):
        if not isinstance(state, (list, tuple, set)):
            state = (state,)
        return self.evaluation_set.filter(task_state__in=state)

    def eval_count(self):
        return len(self.evaluations())

##---MAIN

if __name__ == '__main__':
    pass
