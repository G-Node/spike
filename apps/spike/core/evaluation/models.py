##---IMPORTS

from django.db import models
from django.contrib.contenttypes import generic
from model_utils.fields import Choices
from model_utils.models import StatusModel, TimeStampedModel
from ..signals import sig_evaluation_run, sig_validate_st

__all__ = ['Batch', 'Evaluation']

##---MODELS

class Batch(StatusModel, TimeStampedModel):
    """container for a set of evaluations submitted by a user"""

    ## meta

    class Meta:
        app_label = 'spike'

    ## choices

    STATUS = Choices('private', 'public')

    ## fields

    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        'auth.User',
        blank=True,
        help_text='The user associated with this Batch.')
    algorithm = models.ForeignKey(
        'spike.Algorithm',
        default=1,
        help_text='The Algorithm associated with this Batch.')
    benchmark = models.ForeignKey(
        'spike.Benchmark',
        help_text='The Benchmark associated with this Batch.')

    ## managers

    datafile_set = generic.GenericRelation('spike.Data')

    ## special methods

    def __str__(self):
        return '#%s %s' % (self.pk, self.algorithm)

    def __unicode__(self):
        return unicode(self.__str__())

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'ev_detail', (self.pk,), {}

    @models.permalink
    def get_delete_url(self):
        return 'ev_delete', (self.pk,), {}

    ## interface

    def toggle(self):
        if self.status == self.STATUS.public:
            self.status = self.STATUS.private
        else:
            self.status = self.STATUS.public
        self.save()

    def is_public(self):
        return self.status == self.STATUS.public and self.benchmark.is_public()

    def is_editable(self, user):
        return self.owner == user or user.is_superuser

    def is_accessible(self, user):
        return self.is_public() or self.is_editable(user)


class Evaluation(StatusModel, TimeStampedModel):
    """single trial evaluation object

    When user wants to evaluate the results of his spike sorting work, he
    creates an evaluation. Physically, an evaluation binds together
    user-uploaded file with sorted data, an original version of the raw data
    file and the evaluation results.
    """

    STATUS = Choices('initial', 'running', 'success', 'failure')

    ## meta

    class Meta:
        app_label = 'spike'

    ## fields

    task_id = models.CharField(
        max_length=255,
        blank=True,
        null=True)
    task_log = models.TextField(
        blank=True,
        null=True)
    valid_ev_log = models.TextField(
        blank=True,
        null=True)
    batch = models.ForeignKey('spike.Batch')
    trial = models.ForeignKey('spike.Trial')

    ## managers

    datafile_set = generic.GenericRelation('spike.Data')

    ## special methods

    def __str__(self):
        return '#%s $%s @%s' % (self.batch_id, self.pk, self.trial_id)

    def __unicode__(self):
        return unicode(self.__str__())

    ## interface

    @property
    def ev_file(self):
        try:
            return self.datafile_set.filter(file_type='st_file')[0]
        except IndexError:
            return None

    @property
    def st_file(self):
        try:
            return self.datafile_set.filter(file_type='st_file')[0]
        except IndexError:
            return None

    @property
    def is_valid_ev_file(self):
        if not self.valid_gt_log:
            return False
        if self.valid_gt_log.find('ERROR') >= 0:
            return False
        return True

    def processed(self):
        return self.status == self.STATUS.success

    def is_accessible(self, user):
        return self.batch.is_accessible(user)

    def clear_results(self):
        try:
            self.result_set.all().delete()
        except:
            pass

    def run(self):
        sig_evaluation_run.send_robust(sender=self)

    def validate(self):
        sig_validate_st.send_robust(sender=self)

##---MAIN

if __name__ == '__main__':
    pass
