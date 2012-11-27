##---IMPORTS

from django import template
from ..models import ResultDefaultVisual

register = template.Library()

##---CONSTANTS

KINDS = dict(ResultDefaultVisual.KIND)

##---FILTERS

@register.filter
def sort(qset):
    """return the sorted queryset"""

    return sorted(qset, cmp=lambda a, b: cmp(a.kind, b.kind))

##---TAGS

@register.simple_tag
def result_plot_desc(obj):
    """returns a string describing the result plots"""

    try:
        desc_text = {'wf_single': 'For every neuron in the sorting a piece of data '
                                  'is cut around every of its spikes. This is done for every channel (for '
                                  'multielectrode data) individually. The plot shows all cut spike '
                                  'waveforms superimposed over each other (gray traces). Dashed lines '
                                  'indicate channel boundaries. Colored waveforms represent the average '
                                  'of all spike waveforms (the template) for each neuron.',
                     'wf_all': 'All spike waveforms superimposed.',
                     'clus12': 'The projections of all spikes onto the first two '
                               'principle components is shown. Colors indicate neuron identity. This '
                               'plot gives an impression on how the clusters look like and how good '
                               'their separation (in PCA space) is. To compute this plot principle '
                               'component analysis (PCA) is run on all spike waveforms of the sorting. '
                               'The projections of each waveform is computed on the first two '
                               'principle components.',
                     'clus34': 'This is the same as the previous cluster plot but for PCs 3 and 4.',
                     'clus_proj': 'For each pair of neurons the projections of every '
                                  'spike of both neurons on the vector that connects the templates is '
                                  'shown. This plot is described in Pouzat et al. 2002 "Using noise '
                                  'signature to optimize spike-sorting and to assess neuronal '
                                  'classification quality" (fig. 3 and 6) but here, the noise covariance '
                                  'matrix is not taken into account. Colors indicate neuron identity. The '
                                  'plot gives an impression on how well each pair of clusters is '
                                  'separable. Note however, that the uploaded spike sorting was used to '
                                  'compute this plot, the true separability using the ground truth could '
                                  'be different.',
                     'spiketrain': 'The first second of the spike trains of the sorting '
                                   'are plotted. This plot can be used to see if the website interpreted '
                                   'the uploaded spike train file correctly. Also, if the spike sorter '
                                   'splitted one cluster incorrectly into two (e.g. due to waveform change '
                                   'over time) this is clearly visible in this plot.',
        }.get(obj.kind, 'Could not produce description!')
    except:
        desc_text = 'Could not produce description!'
    finally:
        return '<p>%s</p>' % desc_text

##---MAIN

if __name__ == '__main__':
    pass
