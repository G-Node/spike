##---IMPORTS

from django.db import models
from datetime import datetime
from django.core.files import storage
from django.core.exceptions import MultipleObjectsReturned
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

##---MODEL-REFS

#from spike_evaluation.evaluations.models import Evaluation
Evaluation = models.get_model('evaluations', 'evaluation')

##---MODELS

class FileSystemStorage(storage.FileSystemStorage):
    """subclass of Django's standard FileSystemStorage

    fixes permissions of uploaded files
    """

    def _save(self, name, content):
        name = super(FileSystemStorage, self)._save(name, content)
        full_path = self.path(name)
        mode = getattr(settings, 'FILE_UPLOAD_PERMISSIONS', None)
        if not mode:
            mode = 0644
        os.chmod(full_path, mode)
        return name


class Datafile(models.Model):
    """Datafile is a class representing a data file stored at G-Node."""

    ## choices

    FILETYPE_CHOICES = [
        ('R', 'Rawdata File'),
        ('G', 'Groundtruth File'),
        ('U', 'User Uploaded File'),
    ]

    ## fields

    filetype = models.CharField(max_length=1, choices=FILETYPE_CHOICES)
    record = models.ForeignKey('benchmarks.Record', blank=True)
    date_created = models.DateTimeField(
        _('date created'), default=datetime.now, editable=False)
    added_by = models.ForeignKey('auth.User', blank=True, editable=False)

    ## special methods

    def __unicode__(self):
        return self.name

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'd_download', (), {'did':self.pk}

    ## interface

    def get_version(self, version=None):
        v = None
        try:
            if version:
                v = self.version_set.filter(version=version)[0]
            else:
                vset = self.version_set.filter(validation_state='S')
                if vset:
                    v = vset.order_by('-version')[0]
            if not v:
                v = self.version_set.order_by('-version')[0]
        except MultipleObjectsReturned:
            v = None
        return v

    def get_last_version(self):
        return self.version_set.order_by('-version')[0]

    def get_next_version_index(self):
        return self.version_set.all().count() + 1

    def is_accessible(self, user):
        b = self.record.benchmark
        return b.owner == user or (b.is_active() and self.filetype == 'R')

    def evaluations(self, pub_state=[1]):
        evals = Evaluation.objects.none()
        for v in self.version_set.all():
            evals |= v.evaluations(pub_state=pub_state)
        return evals

    def versions(self):
        return self.version_set.order_by('-version')

    @property
    def name(self):
        return self.get_version().title

    @property
    def size(self):
        return self.get_version().size


class Version(models.Model):
    """implements versioning for datafiles"""

    ## choices

    VALIDATION_STATES = [
        ('I', 'In Progress'),
        ('S', 'Success'),
        ('F', 'Failure'),
    ]

    ## fields

    title = models.CharField(_('title'), max_length=200)
    version = models.IntegerField()
    datafile = models.ForeignKey('Datafile')
    raw_file = models.FileField(_('data file'), upload_to='files/benchmarks/')
    date_created = models.DateTimeField(
        _('date created'), default=datetime.now, editable=False)
    added_by = models.ForeignKey('auth.User', blank=True, editable=False)
    validation_task_id = models.CharField(blank=True, max_length=255)
    validation_state = models.CharField(
        max_length=1, default="I", choices=VALIDATION_STATES)
    validation_log = models.TextField(blank=True, null=True)

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'd_download', (), {'did':self.datafile.id,
                                  'version':self.version}

    ## interface

    def evaluations(self, pub_state=[1]):
        if not isinstance(pub_state, (list, tuple, set)):
            pub_state = list([pub_state])
        return self.evaluation_set.filter(
            publication_state__in=pub_state)

    @property
    def size(self):
        return filesizeformat(self.raw_file.size)

##---MAIN

if __name__ == '__main__':
    pass
