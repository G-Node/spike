##---IMPORTS

from django.db import models

__all__ = ['ResultMetricFFranke']

##---MODEL-REFS

Result = models.get_model('spike', 'result')

##---MODELS

class ResultMetricFFranke(Result):
    """default visual result image"""

    ## meta

    class Meta:
        app_label = 'spike'

    ## fields

    unit_gt = models.CharField(max_length=10)
    unit_ev = models.CharField(max_length=255)
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

        return [self.unit_gt,
                self.unit_ev,
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
