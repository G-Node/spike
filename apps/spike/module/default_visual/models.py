##---IMPORTS

from django.db import models
from model_utils.fields import Choices

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
        (10, 'wf_single'),
        (20, 'wf_all'),
        (30, 'clus12'),
        (40, 'clus34'),
        (50, 'clus_proj'),
        (60, 'spiketrain'),
    )

    ## fields

    file = models.ImageField(upload_to='results/default_visual/%Y/%m/%d/')
    kind = models.IntegerField(choices=KIND)

    ## save and delete

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = ResultDefaultVisual.objects.get(pk=self.pk)
            if orig.file != self.file:
                orig.file.delete(save=False)
        super(ResultDefaultVisual, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete(save=False)
        super(ResultDefaultVisual, self).delete(*args, **kwargs)

##---MAIN

if __name__ == '__main__':
    pass
