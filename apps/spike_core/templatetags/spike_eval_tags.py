##---IMPORTS

from django import template
from django.template.defaultfilters import date
from django.db import models
from ..util import get_pc

register = template.Library()

##---CONSTANTS

User = models.get_model('auth', 'user')
EvaluationResultsImg = models.get_model('spike', 'evaluationresultimg')

##---FILTERS

@register.filter
def is_editable(obj, user):
    if user.is_superuser:
        return True
    if hasattr(obj, 'owner'):
        return obj.owner == user
    if hasattr(obj, 'added_by'):
        return obj.added_by == user


@register.filter
def in_group(user, groups):
    """Returns a boolean if the user is in the given group, or comma-separated
    list of groups.

    Usage::

        {% if user|in_group:"Friends" %}
        ...
        {% endif %}

    or::

        {% if user|in_group:"Friends,Enemies" %}
        ...
        {% endif %}

    """

    rval = False
    try:
        group_list = groups.split(',')
        rval = bool(user.groups.filter(name__in=group_list).values('name'))
    except:
        pass
    finally:
        return rval


@register.filter
def populate(form, instance):
    """populate a model form with an instance"""

    rval = form
    try:
        form = form.__class__(instance=instance)
    except:
        pass
    finally:
        return form


@register.filter
def sorted_plots(res_qset):
    """return the sorted queryset"""

    return sorted(
        res_qset,
        cmp=lambda a, b: cmp(a.order, b.order))

##---TAGS

@register.simple_tag
def state_color(value):
    try:
        ival = int(value)
        if ival >= 0 and ival < 10:
            # in progress
            return 'color: red'
        elif ival >= 10 and ival < 20:
            # failure
            return 'color: blue'
        elif ival >= 20:
            # success
            return 'color: green'
    except:
        return value


@register.simple_tag
def plot_color(value):
    try:
        ival = int(value)
        return get_pc(ival)
    except:
        return '#000000'


@register.simple_tag
def zero_red(value):
    try:
        ival = int(value)
        if ival == 0:
            return 'color: red'
        else:
            return 'color: green'
    except:
        return value


@register.simple_tag
def clear_search_url(request):
    getvars = request.GET.copy()
    if 'search' in getvars:
        del getvars['search']
    if len(getvars.keys()) > 0:
        return "%s?%s" % (request.path, getvars.urlencode())
    else:
        return request.path


@register.simple_tag
def icn_profile(obj):
    if isinstance(obj, User):
        user = obj
    else:
        if hasattr(obj, 'owner'):
            user = obj.owner
        else:
            user = User.objects.get(id=2)
    return """<nobr>
  <i class="icon-user"></i>
  <a href="%s" title="%s">%s</a>
</nobr>""" % (user.get_absolute_url(), user.username, user.username)


@register.simple_tag
def icn_time(obj):
    date_str = None
    try:
        date_str = date(obj)
    except:
        if hasattr(obj, 'created'):
            date_str = date(obj.created)
    finally:
        if not date_str:
            if hasattr(obj, 'created'):
                date_str = date(obj.created)
            else:
                date_str = 'unknown'
    return """<nobr>
  <i class="icon-time"></i>
  <span>%s</span>
</nobr>""" % date_str


@register.simple_tag
def result_plot_desc(obj):
    """returns a string describing the result plots"""

    desc_text = 'Could not produce description!'
    if hasattr(obj, 'file_type'):
        if obj.file_type in ['wf_single', 'wf_all', 'clus12', 'clus34', 'clus_proj', 'spiketrain']:
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
                        }[obj.file_type]
    return '<p>%s</p>' % desc_text
