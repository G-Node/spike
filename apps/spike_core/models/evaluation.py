##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from model_utils.fields import Choices
from model_utils.models import StatusModel, TimeStampedModel

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
    algorithm = models.ForeignKey('Algorithm', default=1)
    benchmark = models.ForeignKey('Benchmark')

    ## managers

    datafile_set = generic.GenericRelation('Datafile')

    ## special methods

    def __str__(self):
        return '#%s %s' % (self.pk, self.algorithm)

    def __unicode__(self):
        return unicode(self.__str__())

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'ev_detail', (), {'btid': self.pk}

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


class Evaluation(TimeStampedModel):
    """single trial evaluation object

    When user wants to evaluate the results of his spike sorting work, he
    creates an evaluation. Physically, an evaluation binds together
    user-uploaded file with sorted data, an original version of the raw data
    file and the evaluation results.
    """

    TASK_STATE_CHOICES = Choices('running', 'success', 'failure')

    ## meta

    class Meta:
        app_label = 'spike'

    ## fields

    task_state = models.CharField(
        choices=TASK_STATE_CHOICES,
        default=TASK_STATE_CHOICES.running,
        max_length=20)
    task_id = models.CharField(
        max_length=255,
        blank=True)
    task_log = models.TextField(
        blank=True,
        null=True)
    batch = models.ForeignKey('Batch')
    trial = models.ForeignKey('Trial')

    ## managers

    datafile_set = generic.GenericRelation('Datafile')

    ## special methods

    def __str__(self):
        return '#%s $%s @%s' % (self.batch_id, self.pk, self.trial_id)

    def __unicode__(self):
        return unicode(self.__str__())

    ## django special methods

    #@models.permalink
    #def get_absolute_url(self):
    #    return 'ev_detail', (), {'evid': self.pk}

    ## interface

    @property
    def ev_file(self):
        try:
            return self.datafile_set.filter(file_type=30)[0]
        except IndexError:
            return None

    def processed(self):
        return self.task_state == 20

    def is_accessible(self, user):
        return self.batch.is_accessible(user)

    def clear_results(self):
        try:
            self.result_set.all().delete()
        except:
            pass

##---MAIN

if __name__ == '__main__':
    pass
