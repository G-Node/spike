##---IMPORTS

from django import template
from django.db import models

register = template.Library()

##---CONSTANTS

Benchmark = models.get_model('spike', 'benchmark')
Evaluation = models.get_model('spike', 'evaluation')
Module = models.get_model('spike', 'module')
Result = models.get_model('spike', 'result')

##---FILTER

@register.filter
def sort(qset):
    try:
        return qset.order_by('id')
    except:
        return qset

##---TAGS

@register.inclusion_tag('spike/module/result_base.html')
def render_results(ev, mod, **kwargs):
    """render tag for results of evaluation for specific module"""

    assert isinstance(ev, Evaluation), 'got ev: %s, expected %s' % (ev.__class__, Evaluation)
    assert isinstance(mod, Module), 'got mod: %s, expected %s' % (mod.__class__, Module)

    tempalte_name = 'spike/module/%s/result.html' % mod.path
    res_list = Result.objects.filter(evaluation=ev, module=mod).select_subclasses()

    return {'template': tempalte_name, 'ev': ev, 'res_list': res_list}


@register.inclusion_tag('spike/module/summary_base.html')
def render_summary(bm, mod, **kwargs):
    """render tag for summary of benchmark for specific module"""

    assert isinstance(bm, Benchmark), 'got ev: %s, expected %s' % (bm.__class__, Benchmark)
    assert isinstance(mod, Module), 'got mod: %s, expected %s' % (mod.__class__, Module)

    tempalte_name = 'spike/module/%s/summary.html' % mod.path
    res_list = Result.objects.filter(evaluation__trial__benchmark=bm, module=mod).select_subclasses()

    return {'template': tempalte_name, 'bm': bm, 'mod': mod, 'res_list': res_list}

##---MAIN

if __name__ == '__main__':
    pass
