##---IMPORTS

from django.conf import  settings
from django.dispatch import receiver
from django.db import models
from .apps.spike.metric.core import Result
from ..tasks import metric_ffranke
from ...core.signals import sig_evaluation_run

__all__ = ['EvaluationResult', 'EvaluationResultImg']

##---CONSTANTS

USE_CELERY = settings.USE_CELERY

##---SIGNAL-HANDLER

@receiver(sig_evaluation_run)
def start_evaluation(sender, **kwargs):
    print 'starting evaluation', sender.id
    if USE_CELERY:
        metric_ffranke.delay(sender.id)
    else:
        metric_ffranke(sender.id)

##---MODELS

class EvaluationResult(Result):
    """evaluation result entity"""

    ## meta

    class Meta:
        app_label = 'spike'

    ## fields

    gt_unit = models.CharField(max_length=10)
    found_unit = models.CharField(max_length=255)
    KS = models.IntegerField(default=0)
    KSO = models.IntegerField(default=0)
    FS = models.IntegerField(default=0)
    TP = models.IntegerField(default=0)
    TPO = models.IntegerField(default=0)
    FPA = models.IntegerField(default=0)
    FPAE = models.IntegerField(default=0)
    FPAO = models.IntegerField(default=0)
    FPAOE = models.IntegerField(default=0)
    FN = models.IntegerField(default=0)
    FNO = models.IntegerField(default=0)
    FP = models.IntegerField(default=0)

    ## interface

    def display(self):
        """display list of numerical results"""
        return [self.gt_unit,
                self.found_unit,
                self.KS,
                self.KS - self.KSO,
                self.KSO,
                self.TP + self.TPO,
                self.TP,
                self.TPO,
                self.FPAE,
                self.FPAOE,
                self.FP,
                self.FPA,
                self.FPAO,
                self.FN,
                self.FNO]

##---MAIN

if __name__ == '__main__':
    pass
