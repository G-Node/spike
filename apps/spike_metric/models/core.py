##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from model_utils.models import TimeStampedModel
from model_utils.managers import InheritanceManager

__all__ = ['Metric', 'Result']

##---MODELS

class Metric(TimeStampedModel):
    """metric model"""

    ## meta

    class Meta:
        app_label = 'spike'

    ## fields

    name = models.CharField(
        max_length=255,
        unique=True,
        blank=False)
    version = models.CharField(
        max_length=32,
        blank=True)
    description = description = models.TextField(
        blank=True)
    exec_name = models.TextField()
    temp_name = models.TextField(blank=True)
    rest_name = models.TextField(blank=True)
    benchmarks = models.ManyToManyField(
        'Benchmark',
        blank=True,
        symmetrical=True)

    ## managers

    datafile_set = generic.GenericRelation('Datafile')

    ## special methods

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return unicode('%s (%s)' % (self.name, self.version))

        ## methods interface


class Result(TimeStampedModel):
    """evaluation result entity"""

    ## meta

    class Meta:
        app_label = 'spike'

    ## fields

    evaluation = models.ForeignKey('Evaluation')
    metric = models.ForeignKey('Metric')

    ## managers

    objects = InheritanceManager()
    datafile_set = generic.GenericRelation('Datafile')

##---MAIN

if __name__ == '__main__':
    pass
