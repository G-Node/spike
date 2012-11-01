##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from model_utils.managers import InheritanceManager
from model_utils.models import TimeStampedModel

from ..util import ACCESS_CHOICES, TASK_STATE_CHOICES

__all__ = ['Result', 'EvaluationResult', 'EvaluationResultImg']

##---MODELS

class Result(TimeStampedModel):
    """evaluation result entity"""

    ## meta

    class Meta:
        app_label = 'spike_eval'

    ## fields

    evaluation = models.ForeignKey('Evaluation')
    metric = models.ForeignKey('Metric')

    ## managers

    objects = InheritanceManager()
    datafile_set = generic.GenericRelation('Datafile')

    ## special methods

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return unicode('=%s %s' % (self.pk, self.evaluation))

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


class EvaluationResult(Result):
    """evaluation result entity"""

    ## meta

    class Meta:
        app_label = 'spike_eval'

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


class EvaluationResultImg(Result):
    """evaluation results picture entity"""

    ## meta

    class Meta:
        app_label = 'spike_eval'

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
