##---IMPORTS

from django.db import models
from django.db.models.signals import post_delete
from model_utils.fields import Choices
from ...models import file_cleanup

__all__ = ['ResultExample']


##---MODEL-REFS

Result = models.get_model('spike', 'result')

##---MODELS

class ResultExample(Result):
    """default visual result image"""

    ## meta

    class Meta:
        app_label = 'spike'

    ## fields

    value = models.IntegerField(default=0)

##---MAIN

if __name__ == '__main__':
    pass
