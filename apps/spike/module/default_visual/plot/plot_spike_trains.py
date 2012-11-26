# -*- coding: utf-8 -*-
#
# spikeval - plot.plot_spike_trains.py
#
# Philipp Meier <pmeier82 at googlemail dot com>
# 2012-08-27
#

"""spike train raster plot"""
__docformat__ = 'restructuredtext'
__all__ = ['spike_trains']


##---IMPORTS

import scipy as sp
from .apps.spike.module.default_visual.plot.common import COLOURS, gen_fig

##---FUNCTION

def spike_trains(spiketrains, spiketrains2=None, alignment=None, marker_width=3, samples_per_second=None,
                 label1=None, label2=None, colours=None):
    """plot one set of spike trains or two sets of spike trains with their inter-spike alignment

    :type spiketrains: dict
    :param spiketrains: Dict of 1d ndarray, holding the spike times.
    :type spiketrains2: dict
    :param spiketrains2: Dict of 1d ndarray, holding the spike times. If this is given an interspike
        assignment plot is created.
    :type alignment: list
    :param alignment: List of lists of tupels containing the pairwise spike alignments.
    :type marker_width: int
    :param marker_width: Fancy parameter for the plot.
    :type samples_per_second: int
    :param samples_per_second: Scale parameter for the axis.
    :type label1: list
    :param label1: Label list for interspike alignment set 1.
    :type label2: list
    :param label2: Label list for interspike alignment set 2.
    :rtype: matplotlib.figure.Figure
    """

    # init and checks
    col_lst = colours or COLOURS
    fig = gen_fig()
    ax = fig.add_subplot(111)
    if not len(spiketrains):
        raise Exception('Provide at least one spiketrain in set 1!')
    nneuron = len(spiketrains)
    srate = float(samples_per_second) or 1.0
    offset = 0
    if spiketrains2 is not None:
        nneuron += len(spiketrains2)
        offset = 1
    labels = []
    idx = 0

    # plot the spike trains
    my_max_timesample = 0
    my_min_timesample = spiketrains[spiketrains.keys()[0]][0]
    for unit in sorted(spiketrains.keys()):
        col = col_lst[idx % len(col_lst)]
        ax.plot(
            spiketrains[unit] / srate,
            sp.zeros_like(spiketrains[unit]) + nneuron - 1 - idx,
            marker='|',
            mec=col,
            mfc=col,
            mew=marker_width,
            ls='None',
            ms=13)
        labels.append('Unit %s' % unit)
        idx += 1
        my_max_timesample = max(my_max_timesample, spiketrains[unit].max())
        my_min_timesample = max(my_min_timesample, spiketrains[unit].min())

    if spiketrains2 is not None:
        labels.append('')
        ax.axhline(y=nneuron - 1 - idx, xmin=0, xmax=1)
        for unit in sorted(spiketrains2.keys()):
            col = col_lst[idx % len(col_lst)]
            ax.plot(
                spiketrains2[unit] / srate,
                sp.zeros_like(spiketrains2[unit]) + nneuron - 1 - idx - offset,
                marker='|',
                mec=col,
                mfc=col,
                mew=marker_width,
                ls='None',
                ms=13)
            labels.append('Unit %s' % unit)
            idx += 1
            my_max_timesample = max(my_max_timesample, spiketrains2[unit].max())
            my_min_timesample = max(my_min_timesample, spiketrains2[unit].min())

    # plot alignment if provided
    if alignment is not None:
        if spiketrains2 is None:
            skeys = sorted(spiketrains.keys())

            for idx1 in xrange(len(skeys)):
                unit1 = skeys[idx1]
                for idx2 in xrange(idx1 + 1, len(skeys)):
                    unit2 = skeys[idx2]
                    for i in xrange(len(alignment[(unit1, unit2)])):
                        start = spiketrains[unit1][
                                alignment[(unit1, unit2)][i][0]] / srate
                        end = spiketrains[unit2][
                              alignment[(unit1, unit2)][i][1]] / srate
                        ax.plot(
                            (start, end),
                            (nneuron - idx1 - 1,
                             nneuron - idx2 - 1),
                            c=(0, 0, 0),
                            ls=":")
        else:
            skeys1 = sorted(spiketrains.keys())
            skeys2 = sorted(spiketrains2.keys())

            for idx1 in xrange(len(skeys1)):
                unit1 = skeys1[idx1]
                for idx2 in xrange(len(skeys2)):
                    unit2 = skeys2[idx2]
                    for i in xrange(len(alignment[(unit1, unit2)])):
                        start = spiketrains[unit1][
                                alignment[(unit1, unit2)][i][0]] / srate
                        end = spiketrains2[unit2][
                              alignment[(unit1, unit2)][i][1]] / srate
                        ax.plot(
                            (start, end),
                            (nneuron - idx1 - 1,
                             nneuron - len(skeys1) -
                             idx2 - 1 - offset),
                            c=(0, 0, 0),
                            ls=":")

    # plot spike labels if provided
    labelList = ['TP', 'TPO', 'FP', 'FPA', 'FPAO', 'FN', 'FNO']
    if label1 is not None:
        idx = 0
        for unit in sorted(spiketrains.keys()):
            for i in xrange(len(label1[unit])):
                if label1[unit][i] - 1 > 1:
                    stri = labelList[label1[unit][i] - 1]
                    ax.text(spiketrains[unit][i] / srate, nneuron - 1 - idx,
                        stri)
            idx += 1
    if label2 is not None and spiketrains2 is not None:
        for unit in sorted(spiketrains2.keys()):
            for i in xrange(len(label2[unit])):
                if label2[unit][i] - 1 > 1:
                    stri = labelList[label2[unit][i] - 1]
                    ax.text(spiketrains2[unit][i] / srate,
                        nneuron - 1 - idx - offset, stri)
            idx += 1

            # beautfy the figure
            #fig_ax.set_title('spiketrains all units')

    if srate is 1:
        ax.set_xlabel('time in samples')
    else:
        ax.set_xlabel('time in seconds')
        #ax.set_ylabel('')
    ax.set_yticks(sp.arange(nneuron + offset) - offset)
    ax.set_yticklabels(labels[::-1])
    ax.set_ylim((-0.5 - offset, nneuron - .5))
    #ax.set_xlim((my_min_timesample-1, my_min_timesample+1))

    # return
    return fig

##---MAIN

if __name__ == '__main__':
    pass
