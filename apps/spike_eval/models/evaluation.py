##---IMPORTS

import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.aggregates import Sum
from django.contrib.contenttypes import generic

from model_utils.models import StatusModel, TimeStampedModel

from ..util import ACCESS_CHOICES, TASK_STATE_CHOICES

__all__ = ['Batch', 'Evaluation']

##---MODELS

class Batch(StatusModel, TimeStampedModel):
    """container for a set of evaluations submitted by a user"""

    ## meta

    class Meta:
        app_label = 'spike_eval'

    ## choices

    STATUS = ACCESS_CHOICES

    ## fields

    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        'auth.User',
        blank=True,
        help_text='The user associated with this Batch.')
    algorithm = models.ForeignKey('Algorithm', default=1)
    benchmark = models.ForeignKey('Benchmark')

    ## managers

    datafile_set = generic.GenericRelation('Datafile')

    ## special methods

    def __str__(self):
        return '#%s %s' % (self.pk, self.algorithm)

    def __unicode__(self):
        return unicode(self.__str__())

    ## django special methods

    @models.permalink
    def get_absolute_url(self):
        return 'ev_detail', (), {'btid': self.pk}

    ## interface

    def toggle(self):
        if self.status == ACCESS_CHOICES.public:
            self.status = ACCESS_CHOICES.private
        else:
            self.status = ACCESS_CHOICES.public
        self.save()

    def is_public(self):
        return self.status == ACCESS_CHOICES.public and self.benchmark.is_public()

    def is_editable(self, user):
        return self.owner == user or user.is_superuser

    def is_accessible(self, user):
        return self.is_public() or self.is_editable(user)

    def summary_table(self):
        rval = []
        for e in self.evaluation_set.all():
            if e.task_state != 20:
                continue
            e_sum = dict(e.summary_table())
            e_sum['trial'] = e.trial.name
            rval.append(e_sum)
        return rval


class Evaluation(TimeStampedModel):
    """single trial evaluation object

    When user wants to evaluate the results of his spike sorting work, he
    creates an evaluation. Physically, an evaluation binds together
    user-uploaded file with sorted data, an original version of the raw data
    file and the evaluation results.
    """

    ## meta

    class Meta:
        app_label = 'spike_eval'

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
    batch = models.ForeignKey('Batch')
    trial = models.ForeignKey('Trial')

    ## managers

    datafile_set = generic.GenericRelation('Datafile')

    ## special methods

    def __str__(self):
        return '#%s $%s @%s' % (self.batch_id, self.pk, self.trial_id)

    def __unicode__(self):
        return unicode(self.__str__())

    ## django special methods

    #@models.permalink
    #def get_absolute_url(self):
    #    return 'ev_detail', (), {'evid': self.pk}

    ## interface

    @property
    def eval_res(self):
        return self.evaluationresults_set.order_by('gt_unit')

    @property
    def eval_res_img(self):
        return self.evaluationresultsimg_set.all()

    @property
    def ev_file(self):
        try:
            return self.datafile_set.filter(file_type=30)[0]
        except IndexError:
            return None

    def processed(self):
        return self.task_state == 20

    def is_accessible(self, user):
        return self.batch.is_accessible(user)

    def clear_results(self):
        self.result_set.all().delete()

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

##---MAIN

if __name__ == '__main__':
    pass
