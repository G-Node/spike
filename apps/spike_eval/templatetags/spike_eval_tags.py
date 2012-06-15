##---IMPORTS

from django import template
from django.template.defaultfilters import date
from django.db import models
from django.core.urlresolvers import reverse

register = template.Library()

##---CONSTANTS

User = models.get_model('auth', 'user')

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
        elif hasattr(obj, 'added_by'):
            user = obj.added_by
        else:
            user = User.objects.get(id=2)
    return """<nobr>
  <i class="icon-user"></i>
  <a href="%s" title="%s">%s</a>
</nobr>""" % (user.get_absolute_url(), user.username, user.username)


@register.simple_tag
def icn_time(obj):
    date_str = 'unknown'
    if hasattr(obj, 'date_created'):
        date_str = date(obj.date_created)
    return """<nobr>
  <i class="icon-time"></i>
  <span>%s</span>
</nobr>""" % date_str
