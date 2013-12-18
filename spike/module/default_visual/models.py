##---IMPORTS

from django.db import models
from django.db.models.signals import post_delete
from model_utils.fields import Choices
from ...models import file_cleanup

__all__ = ['ResultDefaultVisual']


##---MODEL-REFS

Result = models.get_model('spike', 'result')

##---MODELS

class ResultDefaultVisual(Result):
    """default visual result image"""

    ## meta

    class Meta:
        app_label = 'spike'

    ## order

    KIND = Choices(
        (00, 'unknown'),
        (10, 'wf_single'),
        (20, 'wf_all'),
        (30, 'clus12'),
        (40, 'clus34'),
        (50, 'clus_proj'),
        (60, 'spiketrain'),
    )

    ## fields

    file = models.ImageField(upload_to='results/default_visual/')
    kind = models.IntegerField(choices=KIND, default=00)

post_delete.connect(file_cleanup, sender=ResultDefaultVisual, dispatch_uid=__file__)

##---MAIN

if __name__ == '__main__':
    pass
