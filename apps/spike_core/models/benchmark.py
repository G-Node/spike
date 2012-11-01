##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from taggit.managers import TaggableManager
from model_utils.models import StatusModel, TimeStampedModel
from model_utils import Choices

__all__ = ['Benchmark', 'Trial']

##---MODELS

class Benchmark(StatusModel, TimeStampedModel):
    """container for trials

    A Benchmark represents a set of Trials that belong together, and usually
    originate from the same source.
    """

    ## meta

    class Meta:
        app_label = 'spike'

    ## choices

    STATUS = Choices('private', 'public')

    ## fields

    name = models.CharField(
        max_length=255,
        help_text='The name will be used as an identifier for the Benchmark '\
                  'in many places, mostly in links. (character limit: 255)')
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Use this field to give a detailed summary of the '\
                  'Benchmark. If you need to describe more than feasibly can '\
                  'go in this field, please use the Supplementary upload '\
                  'option. (character limit: none)')
    parameter = models.CharField(
        max_length=255,
        default='ID',
        help_text='Trials of the Benchmark will have a parameter attached '\
                  'that can be used to order and distinguish Trials. This is'\
                  ' the caption for that parameter. (character limit: 255)')
    gt_access = models.CharField(
        choices=STATUS,
        default=STATUS.private,
        max_length=20,
        help_text='Access mode for the ground truth files if provided.')
    owner = models.ForeignKey(
        'auth.User',
        blank=True,
        help_text='The user associated with this Benchmark.')

    ## managers

    tags = TaggableManager(
        _('Benchmark Tags'),
        help_text='A comma-separated list of tags classifying the Benchmark.',
        blank=True)
    datafile_set = generic.GenericRelation('Datafile')

    ## special methods

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.name)

    ## django interface

    @models.permalink
    def get_absolute_url(self):
        return 'bm_detail', (), {'bmid': self.pk}

    ## interface

    @property
    def sp_files(self):
        try:
            return self.datafile_set.filter(file_type=40)
        except IndexError:
            return []

    def is_public(self):
        return self.status == Benchmark.STATUS.public

    def is_editable(self, user):
        return self.owner == user or user.is_superuser

    def is_accessible(self, user):
        return self.is_public() or self.is_editable(user)

    def toggle(self):
        if self.status == Benchmark.STATUS.public:
            self.status = Benchmark.STATUS.private
        else:
            self.status = Benchmark.STATUS.public
        self.save()


class Trial(TimeStampedModel):
    """represents an experimental trial

    A Trial consists of raw data and, (if applicable) the corresponding ground
    truth for that raw data. Each is stored in separate files. Raw data is
    generally accessible to the user, while the ground truth is generally
    inaccessible, but can be flagged as available to the user.


    Raw data is stored in hdf5 format, ground truth is stored in gdf format.
    """

    ## meta

    class Meta:
        app_label = 'spike'

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

    ## managers

    datafile_set = generic.GenericRelation('Datafile')

    ## special methods

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.name)

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'bm_trial', (), {'trid': self.pk}

    ## interface

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
