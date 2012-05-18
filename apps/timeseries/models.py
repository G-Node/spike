from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
#from metadata.models import Section
from state_machine.models import SafetyLevel, MetadataManager
from tagging.fields import TagField
from django.conf import settings

from django.utils.translation import ugettext_lazy as _

class TimeSeries(SafetyLevel, MetadataManager):
    # A class representing timeseries data. May be linked to a section in 
    # the metadata.
    TYPES = (
        (10, _('ANALOG')),
        (20, _('SPIKES')),
    )
    ITEMS = (
        (10, _('Hz')),
        (11, _('KHz')),
        (12, _('MHz')),
        (13, _('GHz')),
        (20, _('sec')),
        (21, _('ms')),
        (22, _('mcs')),
        (23, _('ns')),
    )
    title = models.CharField(_('title'), max_length=100)
    caption = models.TextField(_('description'), blank=True)
    date_created = models.DateTimeField(_('date created'), default=datetime.now, editable=False)
    owner = models.ForeignKey(User, editable=False)
    data = models.TextField(_('data'), blank=True)
    data_type = models.IntegerField(_('data type'), choices=TYPES, default=10)
    start_time = models.DateTimeField(_('start time'), default=datetime.now, blank=True)
    time_step = models.IntegerField(_('data timestep'), default=1)
    time_step_items = models.IntegerField(_('units'), choices=ITEMS  , default=21)
    tags = TagField(_('keywords'))

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return ("timeseries_list", [self.pk])
    get_absolute_url = models.permalink(get_absolute_url)

    def get_owner(self):
        return self.owner

    def does_belong_to(self, user):
        if self.owner == user: return True
        return False

    def is_accessible(self, user):
        if (self.owner == user) or (self.is_Public()) or (user in self.shared_with.all()) or (self.is_Friendly() and Friendship.objects.are_friends(user, self.owner)):
            return True
        else:
            return False

    def rename(self, new_title):
        self.title = new_title
        self.save()

    def get_next_counter(self, user):
        """
        Next number to automatically assign as a name to the next Time Serie.
        """
        c = TimeSeries.objects.filter(owner=user).count()
        title = (_("%s") % c)
        while len(title) < 8:
            title = "0" + title
        return title

    def datapoints_count(self):
        """
        Number of datapoints.
        """
        return len(self.data.split(', '))

    def get_data(self):
        return self.data

    def get_data_list(self):
        """
        Returns a list of data values.
        """
        l = []
        for s in self.data.split(', '):
            l.append(float(s))
        return l

    def has_chunks(self):
        """
        True if there is more datapoints than can be displayed on the page.
        """
        if len(self.data.split(', ')) > settings.MAX_DATAPOINTS_DISPLAY:
            return True
        else:
            return False

    def get_data_chunk(self, start_point):
        """
        Returns a chunk of data starting from a given point. Used to display data
        on the page.
        """
        result = ""
        st = start_point
        f1 = self.data.split(', ')
        if self.has_chunks():
            if start_point > 0 and start_point < len(f1):
                if start_point + settings.MAX_DATAPOINTS_DISPLAY < len(f1):
                    f2 = f1[start_point:start_point + settings.MAX_DATAPOINTS_DISPLAY]
                else:
                    f2 = f1[start_point:]
            else:
                f2 = f1[:settings.MAX_DATAPOINTS_DISPLAY]
                st = 0
            for a in f2:
                result += ', ' + str(a)
            result = result[2:]
        else:
            result = self.get_data()
        return result, st

    def get_time_step(self):
        return self.time_step

"""
    def get_data_chunks(self):
        a = 0
        result = []
        data = self.data.split(', ')
        while a < len(data):
            x = data[a:]
            if len(x) < 1000:
                result.append(str(data[a:]))
            else:
                result.append(str(data[a:a+999]))
            a += 1000
        return result"""


