from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from state_machine.models import SafetyLevel, LinkedToProject, MetadataManager
from pinax.apps.projects.models import Project

from tagging.fields import TagField
from django.utils.translation import ugettext_lazy as _

class Experiment(SafetyLevel, LinkedToProject, MetadataManager):
    """
    This class represents an Experiment, hosted at the G-Node.
    """
    title = models.CharField(_('title'), max_length=100)
    caption = models.TextField(_('description'), blank=True)
    date_created = models.DateTimeField(_('date created'), default=datetime.now, editable=False)
    owner = models.ForeignKey(User, blank=True, null=True)
    in_projects = models.ManyToManyField(Project, blank=True, verbose_name=_('related projects'))
    tags = TagField(_('keywords'))

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return ("experiment_details", [self.pk])
    get_absolute_url = models.permalink(get_absolute_url)
