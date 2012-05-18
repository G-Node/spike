from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from state_machine.models import SafetyLevel, LinkedToProject, MetadataManager
from pinax.apps.projects.models import Project

from tagging.fields import TagField
from django.utils.translation import ugettext_lazy as _

class RDataset(SafetyLevel, LinkedToProject, MetadataManager):
    """
    A dataset usually contains files and other objects in one "container" for 
    logical consistency or for further sharing as a single set.
    """
    title = models.CharField(_('title'), max_length=200)
    caption = models.TextField(_('description'), blank=True)
    date_added = models.DateTimeField(_('date added'), default=datetime.now, editable=False)
    owner = models.ForeignKey(User, related_name="added_datasets", blank=True, null=False)
    in_projects = models.ManyToManyField(Project, blank=True, verbose_name=_('related projects'))
    tags = TagField(_('keywords'))

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return ("dataset_details", [self.pk])
    get_absolute_url = models.permalink(get_absolute_url)


