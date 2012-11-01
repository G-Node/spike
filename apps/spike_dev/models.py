##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel
from model_utils.managers import InheritanceManager

##---MODEL-REFS

from spike_core.models import *

##---PROXY-MODELS

from spike_core.models import Benchmark

class BM(Benchmark):
    class Meta:
        proxy = True

from spike_core.models import Trial

class TR(Trial):
    class Meta:
        proxy = True

from spike_datafile.models import Datafile

class DF(Datafile):
    class Meta:
        proxy = True

from spike_core.models import Batch

class BT(Batch):
    class Meta:
        proxy = True


from spike_core.models import Evaluation

class EV(Evaluation):
    class Meta:
        proxy = True

from spike_core.models import Algorithm

class AL(Algorithm):
    class Meta:
        proxy = True

from spike_metric.models import Metric

class MT(Metric):
    class Meta:
        proxy = True

##---MODELS

from spike_metric.models import Result

class ResultTest(Result):
    mini = models.IntegerField()
    maxi = models.IntegerField()
    mean = models.IntegerField()

##---MAIN

if __name__ == '__main__':
    pass
