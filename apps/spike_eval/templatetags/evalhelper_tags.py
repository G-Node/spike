##---IMPORTS

from django import template

register = template.Library()

##---FILTERS

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

##---MAIN

if __name__ == '__main__':
    pass
