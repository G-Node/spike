##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager

__all__ = ['Algorithm']

##---MODELS

class Algorithm(TimeStampedModel):
    """algorithm model"""

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
    owner = models.ForeignKey(
        'auth.User',
        default=2)
    parent = models.ForeignKey(
        'self',
        related_name='children',
        blank=True,
        null=True)

    ## managers

    kind = TaggableManager('Kind')
    datafile_set = generic.GenericRelation('spike.Data')

    ## special methods

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return unicode('%s (%s)' % (self.name, self.version))

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'al_detail', (self.pk,), {}

    @models.permalink
    def get_delete_url(self):
        return 'al_delete', (self.pk,), {}

    ## interface

    def is_editable(self, user):
        return self.owner == user or user.is_superuser

##---MAIN

if __name__ == '__main__':
    pass
