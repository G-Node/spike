# -*- coding: utf-8 -*-
#
# spikeval - plot.plot_cluster_projection.py
#
# Philipp Meier <pmeier82 at googlemail dot com>
# 2012-08-27
#

"""plot projecting whitened cluster data on LDA"""
__docformat__ = 'restructuredtext'
__all__ = ['cluster_projection']


##---IMPORTS

import scipy as sp
from scipy import linalg as sp_la
from scipy.stats import norm
from .apps.spike.module.default_visual.plot.common import COLOURS, gen_fig


##---FUNCTION

def cluster_projection(data, colours=None):
    """produce a plot with the cluster projections according to [citation]

    :type data: dict
    :param data: dict with cluster data in one ndarray (one observation per
        row). This data has to be whitened so the distance measure actually
        make sense!
    :type colours: list
    :param colours: List of colours in any matplotlib conform colour
        representation
        Default=None
    :rtype: matplotlib.figure.Figure
    """

    # init and checks
    col_lst = colours or COLOURS
    fig = gen_fig()
    if not isinstance(data, dict):
        data = {'0': data}
    nu = len(data)
    if nu < 2:
        raise ValueError('only one unit passed!')

    # plot pairwise inter-cluster distributions
    GAUSS_UNIT_SIGMA = norm.pdf(sp.linspace(-4, 4, 51))
    axidx = 0
    for row in xrange(nu - 1):
        for col in xrange(nu - 1 - row):
            # create subplot at correct position
            myax = fig.add_subplot(nu - 1, nu - 1, row * nu + col + 1)
            axidx += 1
            # clusters and cluster means
            clusterA = data[sorted(data.keys())[row]]
            clusterAmean = clusterA.mean(axis=0)
            clusterB = data[sorted(data.keys())[row + col + 1]]
            clusterBmean = clusterB.mean(axis=0)
            # connection vector
            con = clusterAmean - clusterBmean
            con /= sp_la.norm(con)
            # projecton
            clusterAproj = sp.dot(clusterA, con)
            clusterAmean_proj = sp.dot(clusterAmean, con)
            clusterBproj = sp.dot(clusterB, con)
            clusterBmean_proj = sp.dot(clusterBmean, con)
            # plot histograms
            myax.hist(clusterAproj, 50, align='mid', normed=True,
                facecolor=col_lst[row % len(col_lst)],
                edgecolor=col_lst[row % len(col_lst)])
            myax.hist(clusterBproj, 50, align='mid', normed=True,
                facecolor=col_lst[(row + col + 1) % len(col_lst)],
                edgecolor=col_lst[(row + col + 1) % len(col_lst)])
            # plot gauss prototypes
            myax.plot(
                sp.linspace(clusterAmean_proj - 4, clusterAmean_proj + 4, 51),
                GAUSS_UNIT_SIGMA, color='k')
            myax.plot(
                sp.linspace(clusterBmean_proj - 4, clusterBmean_proj + 4, 51),
                GAUSS_UNIT_SIGMA, color='k')
            # jail yaxis
            myax.set_ybound(0.0, 0.5)
            myax.set_yticklabels([])

    # return
    return fig

##---MAIN

if __name__ == '__main__':
    pass
