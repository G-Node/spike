##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from model_utils.models import TimeStampedModel
from .managers import LogManager

__all__ = ['Log', 'LogAnchorMixin']

##---MODELS

class Log(TimeStampedModel):
    """entity: single multiline log string

    `Log`s can be any multiline string. `Log`s can be linked to any entity using a `GenericForeignKey`.
    """

    ## meta

    class Meta:
        app_label = 'spike'

    ## fields

    text = models.TextField()
    kind = models.TextField(
        blank=True,
        null=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    ## managers

    objects = LogManager()

    ## special methods

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return u'Log #%s (%s)' % (self.pk, self.content_object)

    ## url providers

    @models.permalink
    def get_absolute_url(self):
        pass


class LogAnchorMixin(models.Model):
    """mixin providing the data_set relation"""

    ## meta

    class Meta:
        abstract = True

    ## relations

    log_set = generic.GenericRelation('spike.log')

##---MAIN

if __name__ == '__main__':
    pass
