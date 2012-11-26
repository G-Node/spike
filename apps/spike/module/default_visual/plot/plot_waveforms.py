# -*- coding: utf-8 -*-
#
# spikeval - plot.plot_waveforms.py
#
# Philipp Meier <pmeier82 at googlemail dot com>
# 2012-08-27
#

"""waveform plot for extracted spike waveforms"""
__docformat__ = 'restructuredtext'
__all__ = ['waveforms']


##---IMPORTS

import scipy as sp
from .apps.spike.module.default_visual.plot.common import COLOURS, gen_fig

##---FUNCTION

def waveforms(waveforms, samples_per_second=None, tf=None, plot_mean=False, plot_single_waveforms=True,
              set_y_range=False, plot_separate=True, templates=None, colours=None, title=None):
    """plot one set of spiketrains or two sets of spkitrains with their
    interspike alignment

    :type waveforms: dict
    :param waveforms: dict of ndarray, holding the waveforms for different units.
    :type samples_per_second: int
    :param samples_per_second: Scale factor for the axis.
    :type tf: int
    :param tf: The template length of the waveforms
    :type plot_mean: bool
    :param plot_mean: If True, plot the mean-waveform per unit.
    :type plot_single_waveforms: bool
    :param plot_single_waveforms: If True, plot the single waveforms per unit.
    :type plot_separate: bool
    :param plot_separate: If True, plot each units waveforms in a separate axis.
    :type templates: dict
    :param templates: dict holding one concatenates waveform per key
    :type set_y_range: bool
    :param set_y_range: Adjust the y-axis range so waveforms fit in nicely.
    :type colours: list
    :param colours: A list of matplotlib conform color values (rgb 3-tuples). If
        None the common.plot.COLORS set is used.
    :type title: str
    :param title: Title for the plot. No title if None or ''.
    :rtype: matplotlib.figure.Figure
    """

    # init and checks
    col_lst = colours or COLOURS
    fig = gen_fig()
    if plot_separate is False:
        ax = fig.add_subplot(111)
    else:
        ax = None
    if type(waveforms) is not dict:
        waveforms = {'0': waveforms}
    srate = samples_per_second or 1.0
    for k in waveforms.keys():
        if waveforms[k].ndim == 3:
            waveforms[k] = sp.vstack(
                [sp.hstack(
                    [waveforms[k][i, :, j]
                     for j in xrange(waveforms[k].shape[-1])])
                 for i in xrange(waveforms[k].shape[0])])
    firstKey = waveforms.keys()[0]
    nunits = len(waveforms)
    my_ymin = waveforms[firstKey].min()
    my_ymax = waveforms[firstKey].max()
    my_xmax = waveforms[firstKey].shape[1] - 1
    nc = 1
    if tf is not None:
        nc = int(waveforms[firstKey].shape[1] / tf)

    # plot single waveforms
    if plot_single_waveforms is True:
        col_idx = 0
        for u, k in enumerate(sorted(waveforms.keys())):
            if plot_separate is True:
                ax = fig.add_subplot(nunits, 1, u + 1, sharex=ax, sharey=ax)
            nevent, nsample = waveforms[k].shape
            my_ymin = min(my_ymin, waveforms[k].min())
            my_ymax = max(my_ymax, waveforms[k].max())
            my_xmax = max(my_xmax, waveforms[k].shape[1] - 1)
            col = col_lst[col_idx % len(col_lst)]
            if plot_mean is True:
                col = 'gray'
            for i in xrange(waveforms[k].shape[0]):
                ax.plot(sp.arange(nsample) / srate, waveforms[k][i, :],
                    color=col)
            col_idx += 1

            # addition: per axis event count
            ax.set_ylabel('n:%s' % nevent)

    # plot mean waveforms
    if plot_mean is True:
        col_idx = 0
        for u, k in enumerate(sorted(waveforms.keys())):
            if plot_separate is True:
                ax = fig.axes[u]
            if templates is not None and k in templates:
                my_mean = templates[k]
            else:
                my_mean = waveforms[k].mean(axis=0)
            my_ymin = min(my_ymin, my_mean.min())
            my_ymax = max(my_ymax, my_mean.max())
            my_xmax = max(my_xmax, my_mean.size - 1)
            ax.plot(sp.arange(my_mean.size) / srate, my_mean,
                c=col_lst[col_idx % len(col_lst)], lw=2)
            col_idx += 1

    # if multichannel waveforms, plot vertical lines at channel borders
    if tf is not None:
        for i in xrange(1, nc):
            for a in fig.axes:
                a.axvline((tf * i) / srate, ls='dashed', color='y')

    # fancy stuff
    if title is not None:
        fig.suptitle(title)
    if samples_per_second is not None:
        ax.set_xlabel('time [s]')
    else:
        ax.set_xlabel('time [samples]')
    ax.set_xlim(0, my_xmax)
    if set_y_range is True:
        ax.set_ylim((1.01 * my_ymin, 1.01 * my_ymax))

    # return
    return fig

##---MAIN

if __name__ == '__main__':
    pass
