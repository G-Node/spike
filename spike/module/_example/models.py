##---IMPORTS

from django.db import models

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
