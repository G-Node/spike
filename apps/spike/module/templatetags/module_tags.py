##---IMPORTS

from django import template
from django.db import models

register = template.Library()

##---CONSTANTS

Evaluation = models.get_model('spike', 'Evaluation')
Module = models.get_model('spike', 'Module')

##---TAGS

@register.inclusion_tag('spike/module/result_base.html')
def render_results(ev, mod, **kwargs):
    """ template can be Template object or template name """

    assert isinstance(ev, Evaluation), 'got ev: %s, expected %s' % (ev.__class__, Evaluation)
    assert isinstance(mod, Module), 'got mod: %s, expected %s' % (mod.__class__, Module)

    tempalte_name = 'spike/module/%s.html' % mod.path
    res_list = ev.result_set.select_subclasses()

    return {'template': tempalte_name, 'ev': ev, 'res_list': res_list}

##---MAIN

if __name__ == '__main__':
    pass
