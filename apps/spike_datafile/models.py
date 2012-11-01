##---IMPORTS

import hashlib

from django.db import models, signals
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from model_utils.models import TimeStampedModel

__all__ = ['Datafile', 'FileManager']

##---HELPERS

# TODO: get_file_path

##---MANAGER


class DatafileManager(models.Manager):
    def for_obj(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id, object_id=obj.id)

##---MODELS

class Datafile(TimeStampedModel):
    """physical file entity

    `Datafile`s can be any file that needs serving. Initially no assumptions are made about kind of file.
    `Datafile`s will be stored with a hashed filename to prevent double savings. They also provide a
    filetype field to specify the type of file for applications that need to distinguish. `Datafile`s
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
        upload_to='datafile/')
    file_type = models.TextField(
        blank=True,
        null=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    ## managers

    objects = DatafileManager()

    ## special methods

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.name)

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'download', (), {'pk': self.pk}

    ## save and delete

    def save(self, *args, **kwargs):
        print args
        print kwargs
        if self.pk is not None:
            orig = Datafile.objects.get(pk=self.pk)
            if orig.file != self.file:
                orig.file.delete(save=False)
        super(Datafile, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete(save=False)
        super(Datafile, self).delete(*args, **kwargs)

    ## interface

    @property
    def size(self):
        return self.file.size

##---MAIN

if __name__ == '__main__':
    pass
