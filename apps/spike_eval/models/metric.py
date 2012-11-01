##---IMPORTS

import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from model_utils.models import TimeStampedModel

__all__ = ['Metric']

##---MODEL-REFS

Datafile = models.get_model('spike_eval', 'datafile')

##---MODELS

class Metric(TimeStampedModel):
    """metric model"""

    ## meta

    class Meta:
        app_label = 'spike_eval'

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

    ## managers

    datafile_set = generic.GenericRelation('Datafile')

    ## special methods

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return unicode('%s (%s)' % (self.name, self.version))

##---MAIN

if __name__ == '__main__':
    pass
