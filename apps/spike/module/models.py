##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from model_utils.models import TimeStampedModel
from model_utils.managers import InheritanceManager

__all__ = ['Module', 'Result']

##---MODELS

class Module(TimeStampedModel):
    """module model"""

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
        default='0.1')
    description = description = models.TextField(
        blank=True)
    path = models.CharField(
        max_length=255,
        unique=True,
        blank=False)
    benchmarks = models.ManyToManyField(
        'spike.Benchmark',
        blank=True,
        null=True,
        symmetrical=True)
    parent = models.ForeignKey(
        'self',
        related_name='children',
        blank=True,
        null=True)

    ## managers

    datafile_set = generic.GenericRelation('spike.Data')

    ## special methods

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return unicode('%s (%s)' % (self.name, self.version))

    ## methods interface
    pass


class Result(TimeStampedModel):
    """result model - base class"""

    ## meta

    class Meta:
        app_label = 'spike'

    ## fields

    evaluation = models.ForeignKey('spike.Evaluation')
    module = models.ForeignKey('spike.Module')

    ## managers

    objects = InheritanceManager()

##---MAIN

if __name__ == '__main__':
    pass
