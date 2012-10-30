##---IMPORTS

import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.aggregates import Sum

from taggit.managers import TaggableManager

from .common import CommonInfo, DateCreated
from ..util import ACCESS_CHOICES, TASK_STATE_CHOICES

__all__ = ['Algorithm']

##---MODEL-REFS

Datafile = models.get_model('spike_eval', 'datafile')

##---MODELS

class Algorithm(CommonInfo):
    """algorithm model"""

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

    parent = models.ForeignKey(
        'Algorithm',
        blank=True,
        null=True)

    kind = TaggableManager('Kind')

    ## special methods

    def __str__(self):
        return '%s%s' % (self.name,
                         ' (%s)' % self.version if self.version else '')

    def __unicode__(self):
        return unicode(self.__str__())

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'a_detail', (), {'aid': self.pk}

    ## interface

    @property
    def datafile_set(self):
        return Datafile.objects.for_obj(self)


##---MAIN

if __name__ == '__main__':
    pass
