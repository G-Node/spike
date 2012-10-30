##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager

from .common import CommonInfo
from ..util import ACCESS_CHOICES

__all__ = ['Benchmark', 'Trial']

##---MODEL-REFS

Datafile = models.get_model('spike_eval', 'datafile')
Evaluation = models.get_model('spike_eval', 'evaluation')

##---MODELS

class Benchmark(CommonInfo):
    """container for trials

    A Benchmark represents a set of Trials that belong together, and usually
    originate from the same source.
    """

    class Meta:
        app_label = 'spike_eval'

    ## choices

    STATES_CHOICES = [
        (10, 'New'),
        (20, 'Active'),
        (30, 'Closed'),
    ]

    ## fields

    name = models.CharField(
        max_length=255,
        help_text='The name will be used as an identifier for the Benchmark '\
                  'in many places, mostly in links. (character limit: 255)')
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Use this field to give a detailed summary of the '\
                  'Benchmark. If you need to describe more than feasibly can'\
                  ' go in this field, please use the Supplementary upload '\
                  'option. (character limit: none)')
    state = models.IntegerField(
        choices=STATES_CHOICES,
        default=10,
        help_text='The publication state of the Benchmark.')
    parameter = models.CharField(
        max_length=255,
        default='ID',
        help_text='Trials of the Benchmark will have a parameter attached '\
                  'that can be used to order and distinguish Trials. This is'\
                  ' the caption for that parameter. (character limit: 255')
    gt_access = models.IntegerField(
        choices=ACCESS_CHOICES,
        default=10)

    owner = models.ForeignKey(
        'auth.User',
        related_name='benchmark owner',
        blank=True,
        help_text='The user associated with this Benchmark.')

    tags = TaggableManager(
        _('Benchmark Tags'),
        help_text='A comma-separated list of tags classifying the Benchmark.')

    ## special methods

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.__str__())

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'b_detail', (), {'bid': self.pk}

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
            return self.datafile_set.filter(file_type=40)
        except IndexError:
            return []

    def is_active(self):
        return self.state == 20

    def is_accessible(self, user):
        return self.is_active() or self.is_editable(user)

    def is_editable(self, user):
        return self.owner == user or user.is_superuser

    def archive(self):
        self.state = 30
        self.save()

    def resurrect(self):
        self.state = 20
        self.save()

    def eval_batches(self, access=20):
        if not isinstance(access, (list, tuple, set)):
            access = (access,)
        return self.evaluationbatch_set.filter(access__in=access)


class Trial(CommonInfo):
    """represents an experimental trial

    A Trial consists of raw data and, (if applicable) the corresponding ground
    truth for that raw data. Each is stored in separate files. Raw data is
    generally accessible to the user, while the ground truth is generally
    inaccessible, but can be flagged as available to the user.


    Raw data is stored in hdf5 format, ground truth is stored in gdf format.
    """

    ## meta

    class Meta:
        app_label = 'spike_eval'

    ## fields

    name = models.CharField(
        max_length=255,
        help_text='The name will be used as an identifier for the Trial '\
                  'in many places, mostly in links. (character limit: 255)')
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Use this field to give a detailed summary of the Trial. '\
                  '(character limit: none)')
    parameter = models.FloatField(
        default=0.0,
        help_text='The parameter value for this Trial. (type: float)')

    benchmark = models.ForeignKey(
        'Benchmark',
        help_text='The Benchmark associated with this Trial.')

    ## special methods

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.name)

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'b_trial', (), {'tid': self.pk}

    def delete(self, *args, **kwargs):
        self.datafile_set.delete(*args, **kwargs)
        super(Trial, self).delete(*args, **kwargs)

    ## interface

    @property
    def datafile_set(self):
        return Datafile.objects.for_obj(self)

    @property
    def rd_file(self):
        try:
            return self.datafile_set.filter(file_type=10)[0]
        except IndexError:
            return None

    @property
    def gt_file(self):
        try:
            return self.datafile_set.filter(file_type=20)[0]
        except IndexError:
            return None

    def is_validated(self):
        """This indicates whether a trial had even been successfully
        validated, means, at present it still has a successfully validated
        pair of groundtruth - raw data files within different versions of
        related file pairs. That also means this trial is available for
        users to download and perform evaluation against it."""

        try:
            rd_good = self.rd_file.task_state == 20
            gt_good = None
            if self.gt_file:
                gt_good = self.gt_file.task_state == 20
            return rd_good and (gt_good or True)
        except:
            return False

##---MAIN

if __name__ == '__main__':
    pass
