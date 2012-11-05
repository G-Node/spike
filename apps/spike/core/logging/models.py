##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from model_utils.models import TimeStampedModel

__all__ = ['LogItem,', 'LogItemManager']

##---MANAGER


class LogItemManager(models.Manager):
    def for_obj(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id, object_id=obj.id)

##---MODELS

class LogItem(TimeStampedModel):
    """single log entry

    `LogItem`s can be any string that is logging the and attached to the processing of an item. `LogItems`s
    can be linked to any entity using a `GenericForeignKey`.
    """

    ## meta

    class Meta:
        app_label = 'spike'

    ## fields

    text = models.TextField()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    ## managers

    objects = LogItemManager()

    ## special methods

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return u'Log #%s (%s)' % (self.pk, self.content_object)

    ## url providers

    @models.permalink
    def get_absolute_url(self):
        pass

##---MAIN

if __name__ == '__main__':
    pass
