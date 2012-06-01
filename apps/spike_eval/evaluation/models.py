##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.aggregates import Sum

from taggit.managers import TaggableManager

from ..models import CommonInfo, DateCreated
from ..util import ACCESS_CHOICES, TASK_STATE_CHOICES

##---MODEL-REFS

Datafile = models.get_model('datafile', 'datafile')

##---MODELS

class Algorithm(CommonInfo):
    """algorithm model"""

    ## fields

    name = models.CharField(
        max_length=255,
        unique=True,
        blank=False)
    version = models.CharField(
        max_length=32,
        blank=True)
    description = description = models.TextField(
        blank=True)

    parent = models.ForeignKey(
        'Algorithm',
        blank=True,
        null=True)

    kind = TaggableManager('Kind')

    ## special methods

    def __str__(self):
        return '%s%s' % (self.name,
                         ' (%s)' % self.version if self.version else '')

    def __unicode__(self):
        return unicode(self.__str__())


class Evaluation(CommonInfo):
    """single trial evaluation object

    When user wants to evaluate the results of his spike sorting work, he
    creates an evaluation. Physically, an evaluation binds together
    user-uploaded file with sorted data, an original version of the raw data
    file and the evaluation results.
    """

    ## fields

    algorithm = models.ForeignKey(
        Algorithm,
        default=1)
    description = models.TextField(
        blank=True,
        null=True)
    access = models.IntegerField(
        choices=ACCESS_CHOICES,
        default=10)

    task_state = models.IntegerField(
        choices=TASK_STATE_CHOICES,
        default=10)
    task_id = models.CharField(
        max_length=255,
        blank=True)
    task_log = models.TextField(
        blank=True,
        null=True)

    owner = models.ForeignKey(
        'auth.User',
        related_name='evaluation owner',
        blank=True)
    trial = models.ForeignKey(
        'benchmark.Trial')

    ## special methods

    def __str__(self):
        return '%s (#%s)' % (self.algorithm, self.pk)

    def __unicode__(self):
        return unicode(self.__str__())

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'e_detail', (), {'eid':self.pk}

    ## interface

    @property
    def datafile_set(self):
        return Datafile.objects.for_obj(self)

    @property
    def ev_file(self):
        try:
            return self.datafile_set.filter(filetype=30)[0]
        except IndexError:
            return None

    def switch(self):
        if self.access == 10:
            self.access = 20
        else:
            self.access = 10
        self.save()

    def processed(self):
        return self.task_state >= 20

    def is_public(self):
        return self.access == 20

    def is_accessible(self, user):
        return self.owner == user or self.access == 20

    def benchmark(self):
        return self.trial.benchmark

    def summary(self):
        er = self.evaluationresults_set.all()
        if not er:
            return None
        sKS = er.aggregate(Sum("KS")).values()[0]
        sKSO = er.aggregate(Sum("KSO")).values()[0]
        sFS = er.aggregate(Sum("FS")).values()[0]
        sTP = er.aggregate(Sum("TP")).values()[0]
        sTPO = er.aggregate(Sum("TPO")).values()[0]
        sFPA = er.aggregate(Sum("FPA")).values()[0]
        sFPAE = er.aggregate(Sum("FPAE")).values()[0]
        sFPAO = er.aggregate(Sum("FPAO")).values()[0]
        sFPAOE = er.aggregate(Sum("FPAOE")).values()[0]
        sFN = er.aggregate(Sum("FN")).values()[0]
        sFNO = er.aggregate(Sum("FNO")).values()[0]
        sFP = er.aggregate(Sum("FP")).values()[0]

        return {
            'KS':sKS,
            'KSO':sKSO,

            'FS':sFS,

            'TP':sTP,
            'TPO':sTPO,

            'FPAE':sFPAE,
            'FPAOE':sFPAOE,
            'FP':sFP,

            'FPA':sFPA,
            'FPAO':sFPAO,

            'FN':sFN,
            'FNO':sFNO
        }

    def summary_table(self):
        er = self.summary()
        return{'FP':er['FP'],

               'FN':er['FN'] + er['FNO'],
               'FNno':er['FN'],
               'FNo':er['FNO'],

               'FPAE':er['FPAE'] + er['FPAOE'],
               'FPAEno':er['FPAE'],
               'FPAEo':er['FPAOE'],

               'error_sum':er['FP'] + er['FN'] + er['FPAE']}

    def summary_short(self):
        er = self.summary()
        return {
            'TP':(er['TP'] + er['TPO']) / float(er['KS']) * 100,
            'FP':(er['FS'] - er['TP'] - er['TPO']) / float(er['KS']) * 100, }


class EvaluationResults(DateCreated):
    """evaluation result entity"""

    evaluation = models.ForeignKey('Evaluation')
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


class EvaluationResultsImg(DateCreated):
    """evaluation results picture entity"""

    evaluation = models.ForeignKey('Evaluation')
    img_data = models.ImageField(upload_to="files/results/%Y/%m/%d/")
    img_type = models.CharField(max_length=20) # or mapping

##---MAIN

if __name__ == '__main__':
    pass