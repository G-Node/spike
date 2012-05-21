## template filters and tags for the use of SILK ICONS in the SEW

##---IMPORTS

from django import template
from django.conf import settings

register = template.Library()

##---CONSTANTS

ICON_PATH = "%spinax/images/silk/icons/%s.png" % settings.STATIC_URL
ICON_MRKP = """<img class="icon" src="%s" alt="%s" />"""

ICON_SET = {
    # docs
    '':None,
    }

##---FILTERS

@register.simple_tag
def icon(name, alt=''):
    """returns a silk icon for the requested action

    Usage::

        {% icon "<name>" %}
    """

    icon_name = ICON_SET.get(name, None) or name
    rval = ICON_MRKP % (icon_name, alt)
