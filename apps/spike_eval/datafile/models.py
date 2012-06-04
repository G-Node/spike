##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from ..models import CommonInfo
from ..util import FILETYPE_CHOICES, TASK_STATE_CHOICES

##---MANAGER

class DatafileManager(models.Manager):
    def for_obj(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(
            content_type__pk=object_type.id,
            object_id=obj.id)

##---MODELS

class Datafile(CommonInfo):
    """represents a physical file in on the filesystem

    Datafiles can be either raw data files, ground truth files, evaluation
    files or supplementary files. These files are stored in the site_media
    location under the ../spike_eval/.. path.

    Datafiles are only for use with the spike_eval application and should
    only be linked to Benchmark, Trial, Evaluation objects!
    """

    ## managers

    objects = DatafileManager()

    ## fields

    name = models.CharField(
        max_length=255)
    file = models.FileField(
        upload_to='datafile/')
    filetype = models.IntegerField(
        choices=FILETYPE_CHOICES)

    task_state = models.IntegerField(
        choices=TASK_STATE_CHOICES,
        default=10)
    task_id = models.CharField(
        max_length=255,
        blank=True)
    task_log = models.TextField(
        blank=True)

    content_type = models.ForeignKey(
        ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey(
        'content_type',
        'object_id')

    ## special methods

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.name)

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'd_download', (), {'did':self.pk}

    def delete(self, *args, **kwargs):
        # TODO: delete files from filesystem?!
        super(Datafile, self).delete(*args, **kwargs)

    ## interface

    @property
    def size(self):
        return self.file.size

##---MAIN

if __name__ == '__main__':
    pass
