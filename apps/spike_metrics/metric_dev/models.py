##---IMPORTS

from django.conf import  settings
from django.dispatch import receiver
from django.db import models
from ..models import Result
from ..tasks import metric_ffranke
from ...core.signals import sig_evaluation_run

__all__ = ['EvaluationResultImg']

##---CONSTANTS

USE_CELERY = settings.USE_CELERY

##---SIGNAL-HANDLER

@receiver(sig_evaluation_run)
def start_evaluation(sender, **kwargs):
    print 'starting evaluation [picz] (%s)' % sender.id

##---MODELS

class EvaluationResultImg(Result):
    """evaluation results picture entity"""

    ## meta

    class Meta:
        app_label = 'spike'

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
