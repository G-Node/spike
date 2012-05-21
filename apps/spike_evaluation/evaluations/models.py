##---IMPORTS

from datetime import datetime
from django.db import models
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext_lazy as _

##---MODELS

class Evaluation(models.Model):
    """When user wants to evaluate the results of his spike sorting work, he
    creates an evaluation. Physically, an evaluation binds together
    user-uploaded file with sorted data, an original version of the raw data
    file and the evaluation results.
    """

    ## choices

    PROCESSING_STATES = [
        (0, 'Failure'),
        (10, 'In Progress'),
        (20, 'Success'),

    ]
    PUBLICATION_STATES = [
        (0, 'Private'),
        (1, 'Public')
    ]

    ## fields

    algorithm = models.CharField(max_length=100, null=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        'auth.User', related_name='evaluation owner', blank=True)
    user_file = models.FileField(_('sorted data'), upload_to='files/user/')
    original_file = models.ForeignKey('dfiles.Version')
    publication_state = models.IntegerField(choices=PUBLICATION_STATES)
    processing_state = models.IntegerField(
        default=10, choices=PROCESSING_STATES)
    evaluation_task_id = models.CharField(blank=True, max_length=255)
    evaluation_log = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(
        _('date created'), default=datetime.now, editable=False)
    added_by = models.ForeignKey('auth.User', blank=True, editable=False)

    ## special methods

    def __unicode__(self):
        return u'%s (#%s)' % (self.algorithm, self.pk)

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'e_detail', (), {'eid':self.pk}

    ## interface

    def switch(self):
        self.publication_state = (self.publication_state + 1) % 2
        self.save()

    def processed(self):
        return self.processing_state >= 20

    def is_public(self):
        return self.publication_state == 1

    def is_accessible(self, user):
        return self.owner == user or self.is_public()

    def benchmark(self):
        return self.original_file.datafile.record.benchmark

    def record(self):
        return self.original_file.datafile.record

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


class EvaluationResults(models.Model):
    """
    Class for keeping evaluation results.
    """
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
    date_created = models.DateTimeField(
        _('date created'), default=datetime.now, editable=False)

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


class EvaluationResultsImg(models.Model):
    """Evaluation results, pictures"""

    evaluation = models.ForeignKey('Evaluation')
    img_data = models.ImageField(upload_to="files/results/%Y/%m/%d/")
    img_type = models.CharField(max_length=20) # or mapping

##---MAIN

if __name__ == '__main__':
    pass
