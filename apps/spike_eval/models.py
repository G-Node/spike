##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import datetime

##---MODELS

class DateCreated(models.Model):
    """abstract model class for data_created field"""

    ## fields

    date_created = models.DateTimeField(
        _("date created"),
        default=datetime.now,
        editable=False)

    ## meta

    class Meta:
        abstract = True


class AddedBy(models.Model):
    """abstract model class for added_by field"""

    ## fields

    added_by = models.ForeignKey(
        'auth.User',
        blank=True,
        null=True,
        editable=False)

    ## meta

    class Meta:
        abstract = True


class CommonInfo(AddedBy, DateCreated):
    """abstract base class for date_created and added_by field"""

    ## meta

    class Meta:
        abstract = True

##---MAIN

if __name__ == '__main__':
    pass
