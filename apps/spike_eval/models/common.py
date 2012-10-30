##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import datetime

__all__ = ['DateCreated', 'AddedBy', 'CommonInfo']

##---MODELS

class DateCreated(models.Model):
    """abstract model class for data_created field"""

    ## meta

    class Meta:
        abstract = True
        app_label = 'spike_eval'

    ## fields

    date_created = models.DateTimeField(
        _("date created"),
        default=datetime.now,
        editable=False)


class AddedBy(models.Model):
    """abstract model class for added_by field"""

    ## meta

    class Meta:
        abstract = True
        app_label = 'spike_eval'

    ## fields

    added_by = models.ForeignKey(
        'auth.User',
        blank=True,
        null=True,
        editable=False)


class CommonInfo(AddedBy, DateCreated):
    """abstract base class for date_created and added_by field"""

    ## meta

    class Meta:
        abstract = True
        app_label = 'spike_eval'

##---MAIN

if __name__ == '__main__':
    pass
