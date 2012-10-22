##---IMPORTS

from django.shortcuts import render_to_response
from django.template import RequestContext

##---CHOICES

ACCESS_CHOICES = [
    (10, 'PRIVATE'),
    (20, 'PUBLIC'),
]

FILETYPE_CHOICES = [
    (10, 'Rawdata File'),
    (20, 'Groundtruth File'),
    (30, 'Evaluation File'),
    (40, 'Supplementary File'),
]

TASK_STATE_CHOICES = [
    (10, 'Running'),
    (20, 'Success'),
    (30, 'Failure'),
]

##---COLOR-PALETTE

PLOT_COLORS = [
    '#FF0000', # 01 red
    '#00FF00', # 02 green
    '#0000FF', # 03 blue
    '#FF00FF', # 04 magenta
    '#FFFF00', # 05 yellow
    '#00FFFF', # 06 cyan
    '#9900FF', # 07 aubergine
    '#FF9900', # 08 orange
    '#00FF99', # 09 mint
    '#FF0099', # 10 pink
    '#99FF00', # 11 neon
    '#0099FF', # 12 ocean
]
N_PLOT_COLORS = len(PLOT_COLORS)
get_pc = lambda n: PLOT_COLORS[n % N_PLOT_COLORS]

##---DECORATORS

def render_to(template_name):
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if not isinstance(output, dict):
                return output
            return render_to_response(
                template_name,
                output,
                context_instance=RequestContext(request))

        return wrapper

    return renderer

##---MAIN

if __name__ == '__main__':
    pass
