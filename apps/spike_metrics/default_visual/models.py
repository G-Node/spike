##---IMPORTS

from django.db import models

__all__ = ['EvaluationResultImg']

##---MODELS

class MR_default_visual(Result):
    """default visual result image"""

    ## meta

    class Meta:
        app_label = 'spike_metrics'

    ## order

    order_dict = {
        'wf_single': 0,
        'wf_all': 1,
        'clus12': 2,
        'clus34': 3,
        'clus_proj': 4,
        'spiketrain': 5,
    }

    ## fields

    file = models.ImageField(upload_to='results/%Y/%m/%d/')
    file_type = models.CharField(max_length=20) # or mapping

    ## interface

    @property
    def order(self):
        try:
            return self.order_dict[self.file_type]
        except:
            return 999

    ## save and delete

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = EvaluationResultImg.objects.get(pk=self.pk)
            if orig.file != self.file:
                orig.file.delete()
        super(EvaluationResultImg, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete()
        super(EvaluationResultImg, self).delete(*args, **kwargs)

##---MAIN

if __name__ == '__main__':
    pass
