##---IMPORTS

import os

from django.db import models
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

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'a_detail', (), {'aid': self.pk}

    ## interface

    @property
    def datafile_set(self):
        return Datafile.objects.for_obj(self)


class EvaluationBatch(CommonInfo):
    """set of evaluations from a submission"""

    ## fields
    description = models.TextField(blank=True, null=True)
    access = models.IntegerField(choices=ACCESS_CHOICES, default=10)

    algorithm = models.ForeignKey('Algorithm', default=1)
    benchmark = models.ForeignKey('benchmark.Benchmark')

    ## special methods

    def __str__(self):
        return 'Batch #%s (%s)' % (self.pk, self.algorithm)

    def __unicode__(self):
        return unicode(self.__str__())

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'e_batch', (), {'ebid': self.pk}

    ## interface

    @property
    def datafile_set(self):
        return Datafile.objects.for_obj(self)

    def switch(self):
        if self.access == 10:
            self.access = 20
        else:
            self.access = 10
        self.save()

    def is_public(self):
        return self.access == 20

    def is_accessible(self, user):
        return self.is_public() or self.is_editable(user)

    def is_editable(self, user):
        return self.added_by == user or user.is_superuser

    def summary_table(self):
        rval = []
        for e in self.evaluation_set.all():
            if e.task_state != 20:
                continue
            e_sum = dict(e.summary_table())
            e_sum['trial'] = e.trial.name
            rval.append(e_sum)
        return rval

    ## save and delete

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = EvaluationBatch.objects.get(pk=self.pk)
            if orig.datafile_set:
                for df in orig.datafile_set:
                    if df not in self.datafile_set:
                        df.delete()
        super(EvaluationBatch, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.datafile_set.delete()
        super(EvaluationBatch, self).delete(*args, **kwargs)


class Evaluation(CommonInfo):
    """single trial evaluation object

    When user wants to evaluate the results of his spike sorting work, he
    creates an evaluation. Physically, an evaluation binds together
    user-uploaded file with sorted data, an original version of the raw data
    file and the evaluation results.
    """

    ## fields

    task_state = models.IntegerField(
        choices=TASK_STATE_CHOICES,
        default=10)
    task_id = models.CharField(
        max_length=255,
        blank=True)
    task_log = models.TextField(
        blank=True,
        null=True)

    evaluation_batch = models.ForeignKey('EvaluationBatch')
    trial = models.ForeignKey('benchmark.Trial')

    ## special methods

    def __str__(self):
        return 'Evaluation #%s @%s' % (self.pk, self.evaluation_batch_id)

    def __unicode__(self):
        return unicode(self.__str__())

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'e_detail', (), {'eid': self.pk}

    ## interface

    @property
    def eval_res(self):
        return self.evaluationresults_set.order_by('gt_unit')

    @property
    def eval_res_img(self):
        return self.evaluationresultsimg_set.all()

    @property
    def datafile_set(self):
        return Datafile.objects.for_obj(self)

    @property
    def ev_file(self):
        try:
            return self.datafile_set.filter(file_type=30)[0]
        except IndexError:
            return None

    @property
    def benchmark(self):
        return self.trial.benchmark

    def processed(self):
        return self.task_state == 20

    def is_accessible(self, user):
        return self.evaluation_batch.is_accessible(user)

    def clear_results(self):
        self.evaluationresults_set.all().delete()
        self.evaluationresultsimg_set.all().delete()

    def summary(self):
        er = self.evaluationresults_set.all()
        if not er:
            return None
        sKS = er.aggregate(Sum('KS')).values()[0]
        sKSO = er.aggregate(Sum('KSO')).values()[0]
        sFS = er.aggregate(Sum('FS')).values()[0]
        sTP = er.aggregate(Sum('TP')).values()[0]
        sTPO = er.aggregate(Sum('TPO')).values()[0]
        sFPA = er.aggregate(Sum('FPA')).values()[0]
        sFPAE = er.aggregate(Sum('FPAE')).values()[0]
        sFPAO = er.aggregate(Sum('FPAO')).values()[0]
        sFPAOE = er.aggregate(Sum('FPAOE')).values()[0]
        sFN = er.aggregate(Sum('FN')).values()[0]
        sFNO = er.aggregate(Sum('FNO')).values()[0]
        sFP = er.aggregate(Sum('FP')).values()[0]

        return {
            'KS': sKS,
            'KSO': sKSO,

            'FS': sFS,

            'TP': sTP,
            'TPO': sTPO,

            'FPAE': sFPAE,
            'FPAOE': sFPAOE,
            'FP': sFP,

            'FPA': sFPA,
            'FPAO': sFPAO,

            'FN': sFN,
            'FNO': sFNO
        }

    def summary_table(self):
        er = self.summary()
        return{'FP': er['FP'],

               'FN': er['FN'] + er['FNO'],
               'FNno': er['FN'],
               'FNo': er['FNO'],

               'FPAE': er['FPAE'] + er['FPAOE'],
               'FPAEno': er['FPAE'],
               'FPAEo': er['FPAOE'],

               'error_sum': er['FP'] + er['FN'] + er['FPAE']}

    def summary_short(self):
        er = self.summary()
        return {
            'TP': (er['TP'] + er['TPO']) / float(er['KS']) * 100,
            'FP': (er['FS'] - er['TP'] - er['TPO']) / float(er['KS']) * 100, }

    ## save and delete

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = Evaluation.objects.get(pk=self.pk)
            if orig.ev_file.file != self.ev_file.file:
                orig.ev_file.delete()
        super(Evaluation, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        self.ev_file.delete()
        super(Evaluation, self).delete(*args, **kwargs)


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

    ## special methods

    def __str__(self):
        return 'EvaluationResults #%s @%s' % (self.pk, self.evaluation_id)

    def __unicode__(self):
        return unicode(self.__str__())

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


class EvaluationResultsImg(DateCreated):
    """evaluation results picture entity"""

    order_dict = {
        'wf_single': 0,
        'wf_all': 1,
        'clus12': 2,
        'clus34': 3,
        'clus_proj': 4,
        'spiketrain': 5,
    }

    evaluation = models.ForeignKey('Evaluation')
    img_data = models.ImageField(upload_to='results/%Y/%m/%d/')
    img_type = models.CharField(max_length=20) # or mapping

    ## special methods

    def __str__(self):
        return 'EvaluationResultsImg #%s @%s' % (self.pk, self.evaluation_id)

    def __unicode__(self):
        return unicode(self.__str__())

    ## interface

    @property
    def order(self):
        try:
            return self.order_dict[self.img_type]
        except:
            return 999

    ## save and delete

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = EvaluationResultsImg.objects.get(pk=self.pk)
            if orig.file != self.file:
                orig.file.delete()
        super(EvaluationResultsImg, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete()
        super(EvaluationResultsImg, self).delete(*args, **kwargs)

##---MAIN

if __name__ == '__main__':
    pass
