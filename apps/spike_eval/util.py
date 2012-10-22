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

    #'#FF0000', # 01 red
    #'#00FF00', # 02 green
    #'#0000FF', # 03 blue
    #'#FF00FF', # 04 magenta
    #'#FFFF00', # 05 yellow
    #'#00FFFF', # 06 cyan
    #'#9900FF', # 07 aubergine
    #'#FF9900', # 08 orange
    #'#00FF99', # 09 mint
    #'#FF0099', # 10 pink
    #'#99FF00', # 11 neon
    #'#0099FF', # 12 ocean

    '#990F0F', #153      15      15
    '#6B990F', #107     153      15
    '#0F6B99', #15     107     153
    '#99540F', #153      84      15
    '#260F99', #38      15     153
    '#B22C2C', #178      44      44
    '#85B22C', #133     178      44
    '#2C85B2', #44     133     178
    '#B26F2C', #178     111      44
    '#422CB2', #66      44     178
    '#CC5151', #204      81      81
    '#A3CC51', #163     204      81
    '#51A3CC', #81     163     204
    '#CC8E51', #204     142      81
    '#6551CC', #101      81     204
    '#E57E7E', #229     126     126
    '#C3E57E', #195     229     126
    '#7EC3E5', #126     195     229
    '#E5B17E', #229     177     126
    '#8F7EE5', #143     126     229
    '#FFB2B2', #255     178     178
    '#E5FFB2', #229     255     178
    '#B2E5FF', #178     229     255
    '#FFD8B2', #255     216     178
    '#BFB2FF', #191     178     255
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
