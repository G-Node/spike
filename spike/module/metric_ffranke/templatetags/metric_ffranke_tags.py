##---IMPORTS

from django import template
from django.db.models.aggregates import Sum

register = template.Library()

##---FILTERS

@register.filter
def sort(qset):
    """return the sorted queryset"""

    return qset.order_by('resultmetricffranke__unit_gt')


@register.filter
def summary(qset):
    """summary from result queryset"""

    # early exit
    if not qset:
        return None

    # aggregate
    sKS = qset.aggregate(Sum('resultmetricffranke__KS')).values()[0]
    sKSO = qset.aggregate(Sum('resultmetricffranke__KSO')).values()[0]
    sFS = qset.aggregate(Sum('resultmetricffranke__FS')).values()[0]
    sTP = qset.aggregate(Sum('resultmetricffranke__TP')).values()[0]
    sTPO = qset.aggregate(Sum('resultmetricffranke__TPO')).values()[0]
    sFPA = qset.aggregate(Sum('resultmetricffranke__FPA')).values()[0]
    sFPAE = qset.aggregate(Sum('resultmetricffranke__FPAE')).values()[0]
    sFPAO = qset.aggregate(Sum('resultmetricffranke__FPAO')).values()[0]
    sFPAOE = qset.aggregate(Sum('resultmetricffranke__FPAOE')).values()[0]
    sFN = qset.aggregate(Sum('resultmetricffranke__FN')).values()[0]
    sFNO = qset.aggregate(Sum('resultmetricffranke__FNO')).values()[0]
    sFP = qset.aggregate(Sum('resultmetricffranke__FP')).values()[0]

    # return dict
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


@register.filter
def summary_table(qset):
    """summary table from result queryset"""

    # early exit
    if not qset:
        return None
    qs_sum = summary(qset)
    if not qs_sum:
        return None

    # return dict
    return {'FP': qs_sum['FP'],

            'FN': qs_sum['FN'] + qs_sum['FNO'],
            'FNno': qs_sum['FN'],
            'FNo': qs_sum['FNO'],

            'FPAE': qs_sum['FPAE'] + qs_sum['FPAOE'],
            'FPAEno': qs_sum['FPAE'],
            'FPAEo': qs_sum['FPAOE'],

            'error_sum': qs_sum['FP'] + qs_sum['FN'] + qs_sum['FPAE']}


@register.filter
def summary_short(qset):
    """short summary from result queryset"""

    # early exit
    if not qset:
        return None
    qs_sum = summary(qset)
    if not qs_sum:
        return None

    # result dict
    return {
        'TP': (qs_sum['TP'] + qs_sum['TPO']) / float(qs_sum['KS']) * 100,
        'FP': (qs_sum['FS'] - qs_sum['TP'] - qs_sum['TPO']) / float(qs_sum['KS']) * 100, }

##---MAIN

if __name__ == '__main__':
    pass
sum
