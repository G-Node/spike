##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.signals import post_delete
from ..models import file_cleanup

from model_utils.models import TimeStampedModel
from .managers import DataManager

__all__ = ['Data', 'DataAnchorMixin']

##---MODELS

class Data(TimeStampedModel):
    """entity: physical file

    `Data`s can be any physical file that needs serving. Initially no assumptions are made about the kind
    or format of the file. `Data`s will be stored on diskwith a hashed filename to prevent double savings. They also provide a
    filetype field to specify the type of file for applications that need to distinguish. `Data`s
    can be linked to any entity using a `GenericForeignKey`.
    """

    ## meta

    class Meta:
        app_label = 'spike'

    ## fields

    name = models.CharField(
        max_length=255)
    ext = models.CharField(
        max_length=40,
        blank=True,
        null=True)
    sha1 = models.CharField(
        max_length=40,
        blank=True,
        null=True)
    file = models.FileField(
        upload_to='data/')
    kind = models.TextField(
        blank=True,
        null=True)
    # generic foreign key
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    ## managers

    objects = DataManager()

    ## special methods

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.name)

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'dt_download', (self.pk,), {}

    @models.permalink
    def get_delete_url(self):
        return 'dt_delete', (self.pk,), {}

    ## interface

    @property
    def size(self):
        return self.file.size

post_delete.connect(file_cleanup, sender=Data, dispatch_uid=__file__)


class DataAnchorMixin(models.Model):
    """mixin providing the data_set relation"""

    ## meta

    class Meta:
        abstract = True

    ## relations

    data_set = generic.GenericRelation('spike.data')

##---MAIN

if __name__ == '__main__':
    pass
