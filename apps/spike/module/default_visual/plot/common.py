# -*- coding: utf-8 -*-
#
# spikeval - plot.common.py
#
# Philipp Meier <pmeier82 at googlemail dot com>
# 2012-08-27
#

"""basic stuff for plotting"""
__docformat__ = 'restructuredtext'
__all__ = ['COLOURS', 'gen_fig']


##---IMPORTS

import os
from matplotlib.figure import Figure

##---CONSTANTS

COLOURS = [
    (0.0, 0.0, 1.0), # blue
    (0.0, 1.0, 0.0), # green
    (1.0, 0.0, 0.0), # red
    (1.0, 0.0, 1.0), # fuchsia
    (0.0, 1.0, 1.0), # aqua
    (0.5, 0.5, 0.5), # gray
    (1.0, 1.0, 0.0), # yellow
    (0.5, 0.5, 0.0), #
    (1.0, 0.5, 0.5), #
    (0.5, 1.0, 0.5), #
    (0.0, 0.0, 0.5), # navy
    (0.0, 0.5, 0.0), # green
    (0.5, 0.0, 0.0), # maroon
    (0.0, 0.5, 0.5), # teal
    (0.5, 0.0, 0.5), # purple
    (0.5, 0.5, 0.0), # olive
    (0.2, 0.5, 0.8), #
    (1.0, 0.1, 0.1), #
    (0.3, 0.3, 0.3), #
    (0.0, 0.0, 0.0), # black
    (0.9, 0.2, 0.9), #
    (0.2, 0.9, 0.9), #
    (0.9, 0.9, 0.2), #
]
"""list of RGB tuples to use for unified colours across the plots

usage:
    for i in xrange(huge_number):
        ax.plot(myline[i], c=COLOURS[i%NCOL])
"""


##---FUNCTIONS

def gen_fig(**kwargs):
    """generate a matplotlib figure instance to be used as a plotting context"""

    fig = Figure(**kwargs)
    return fig

##---MAIN

if __name__ == '__main__':
    pass
