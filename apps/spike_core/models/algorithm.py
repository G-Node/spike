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
        blank=True,
        help_text='The user associated with this Algorithm.')
    parent = models.ForeignKey(
        'Algorithm',
        related_name='children',
        blank=True,
        null=True)

    ## managers

    kind = TaggableManager('Kind')
    datafile_set = generic.GenericRelation('Datafile')

    ## special methods

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return unicode('%s (%s)' % (self.name, self.version))

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'al_detail', (), {'alid': self.pk}

##---MAIN

if __name__ == '__main__':
    pass
