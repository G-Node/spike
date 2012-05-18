import tarfile
import zipfile
try:
    import json
except ImportError:
    import simplejson as json

from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from state_machine.models import SafetyLevel, LinkedToProject, MetadataManager
from django.core.files import storage
from django.template.defaultfilters import filesizeformat
from friends.models import Friendship
from pinax.apps.projects.models import Project
from tagging.fields import TagField
from django.utils.translation import ugettext_lazy as _
import settings

def make_upload_path(self, filename):
    """
    Generates upload path for FileField.
    """
    return "data/%s/%s" % (self.owner.username, filename)

# set up the location to store USER FILES
try:
    location = settings.FILE_MEDIA_ROOT
except:
    location = "/data/media/"
fs = storage.FileSystemStorage(location=location)

class FileSystemStorage(storage.FileSystemStorage):
    """
    Subclass Django's standard FileSystemStorage to fix permissions
    of uploaded files.
    """
    def _save(self, name, content):
        name =  super(FileSystemStorage, self)._save(name, content)
        full_path = self.path(name)
        mode = getattr(settings, 'FILE_UPLOAD_PERMISSIONS', None)
        if not mode:
            mode = 0644
        os.chmod(full_path, mode)
        return name

class Datafile(SafetyLevel, LinkedToProject, MetadataManager):
    """
    Datafile is a class representing a data file stored at G-Node.
    """
    title = models.CharField(_('name'), blank=True, max_length=200)
    caption = models.TextField(_('description'), blank=True)
    date_added = models.DateTimeField(_('date added'), default=datetime.now, editable=False)
    owner = models.ForeignKey(User, related_name="related_file", blank=True, null=True)
    in_projects = models.ManyToManyField(Project, blank=True, verbose_name=_('related projects'))
    raw_file = models.FileField(_('data file'), storage=fs, upload_to="data/") # or make_upload_path.. which doesn't work in PROD due to python2.5
    tags = TagField(_('keywords'))
    # here we put file info extracted using neuroshare, stored as JSON
    extracted_info = models.TextField('extracted_info', blank=True, null=True)
    # indicate whether the file is convertible using NEO / Neuroshare
    convertible = models.NullBooleanField('convertible', blank=True, null=True)
    # store ID of the last Task Broker task
    last_task_id = models.CharField('last_task_id', blank=True, max_length=255)
    # indicate whether some information was extracted from file (if archive)
    extracted = models.CharField('extracted', default="virgin", max_length=20)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return ("datafile_details", [self.pk])
    get_absolute_url = models.permalink(get_absolute_url)

    @property
    def size(self):
        return filesizeformat(self.raw_file.size)

    @property
    def info(self):
        if self.extracted_info:
            return json.loads(self.extracted_info)
        else:
            return None

    @property
    def is_archive(self):
        if tarfile.is_tarfile(self.raw_file.path) or \
            zipfile.is_zipfile(self.raw_file.path):
            return True
        return False

