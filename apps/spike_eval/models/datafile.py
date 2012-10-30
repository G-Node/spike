##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from .common import CommonInfo
from ..util import FILETYPE_CHOICES, TASK_STATE_CHOICES

__all__ = ['Datafile', 'DatafileManager']

##---MANAGER

class DatafileManager(models.Manager):
    def for_obj(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id, object_id=obj.id)

##---MODELS

class Datafile(CommonInfo):
    """represents a physical file in on the filesystem

    Datafiles can be either raw data files, ground truth files, evaluation
    files or supplementary files. These files are stored in the site_media
    location under the ../spike_eval/.. path.

    Datafiles are only for use with the spike_eval application and should
    only be linked to Benchmark, Trial, Evaluation objects!
    """

    ## meta

    class Meta:
        app_label = 'spike_eval'

    ## managers

    objects = DatafileManager()

    ## fields

    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='results/%Y/%m/%d/')
    file_type = models.IntegerField(choices=FILETYPE_CHOICES, default=0)

    task_state = models.IntegerField(choices=TASK_STATE_CHOICES, default=10)
    task_id = models.CharField(max_length=255, blank=True)
    task_log = models.TextField(blank=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    ## special methods

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.name)

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'd_download', (), {'did': self.pk}

    ## save and delete

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = Datafile.objects.get(pk=self.pk)
            if orig.file != self.file:
                orig.file.delete()
        super(Datafile, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete()
        super(Datafile, self).delete(*args, **kwargs)

    ## interface

    @property
    def size(self):
        return self.file.size

##---MAIN

if __name__ == '__main__':
    pass
