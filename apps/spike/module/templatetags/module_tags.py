##---IMPORTS

from django import template
from django.db import models

register = template.Library()

##---CONSTANTS

Evaluation = models.get_model('spike', 'Evaluation')
Module = models.get_model('spike', 'Module')
Result = models.get_model('spike', 'Result')

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

    tempalte_name = 'spike/module/%s.html' % mod.path
    res_list = Result.objects.filter(evaluation=ev, module=mod).select_subclasses()

    return {'template': tempalte_name, 'ev': ev, 'res_list': res_list}

##---MAIN

if __name__ == '__main__':
    pass
