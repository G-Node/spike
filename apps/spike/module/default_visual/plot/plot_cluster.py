# -*- coding: utf-8 -*-
#
# spikeval - plot.plot_cluster.py
#
# Philipp Meier <pmeier82 at googlemail dot com>
# 2012-08-27
#

"""scatter plot for cluster data"""
__docformat__ = 'restructuredtext'
__all__ = ['cluster']


##---IMPORTS

from matplotlib.patches import Ellipse
from .apps.spike.module.default_visual.plot.common import COLOURS, gen_fig

##---FUNCTION

def cluster(data, data_dim=(0, 1), plot_mean=True, colours=None, title=None, xlabel=None, ylabel=None):
    """plot a set of clusters with different colors each

    :type data: object
    :param data: Preferably a dictionary with ndarray entries.
    :type data_dim: tuple
    :param data_dim: A 2-tuple giving the dimension (entries per datapoint/
        columns) to use for the scatter plot of the cluster.
        Default=(0,1)
    :type plot_mean: bool or float
    :param plot_mean: If False, do nothing. If True or positive integer, plot
        the cluster means with a strong cross, if positive float, additionally
        plot a unit circle of that radius (makes sense for prewhitened pca
        data), thus interpreting the value as the std of the cluster.
        Default=True
    :type colours: list
    :param colours: List of colors in any matplotlib conform colour representation.
        Default=None
    :type title: str
    :param title: A title for the plot. No title if None or ''.
    :type xlabel: str
    :param xlabel: A label for the x-axis. No label if None or ''.
    :type ylabel: str
    :param ylabel: A label for the y-axis. No label if None or ''.
    :rtype: matplotlib.figure.Figure
    """

    # init and checks
    col_lst = colours or COLOURS
    fig = gen_fig()
    ax = fig.add_subplot(111)
    if not isinstance(data, dict):
        data = {'0': data} # str(0) ??

    # plot single cluster members
    col_idx = 0
    for k in sorted(data.keys()):
        ax.plot(
            data[k][:, data_dim[0]],
            data[k][:, data_dim[1]],
            marker='.',
            lw=0,
            c=col_lst[col_idx % len(col_lst)])
        col_idx += 1

    # plot cluster means
    if plot_mean is not False:
        col_idx = 0
        for k in sorted(data.keys()):
            mean_k = data[k][:, data_dim].mean(axis=0)
            ax.plot(
                [mean_k[0]],
                [mean_k[1]],
                lw=0,
                marker='x',
                mfc=col_lst[col_idx % len(col_lst)],
                ms=10,
                mew=1,
                mec='k')

            # plot density estimates
            if plot_mean is not True:
                ax.add_artist(
                    Ellipse(
                        xy=mean_k,
                        width=plot_mean * 2,
                        height=plot_mean * 2,
                        facecolor='none',
                        edgecolor=col_lst[col_idx % len(col_lst)]))
            col_idx += 1

    # fancy stuff
    if title is not None:
        ax.set_title(title)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)

    # return
    return fig

##---MAIN

if __name__ == '__main__':
    pass
