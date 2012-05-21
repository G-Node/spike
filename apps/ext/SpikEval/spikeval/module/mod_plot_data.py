# -*- coding: utf-8 -*-
#
# spikeval - module.mod_plot_data.py
#
# Philipp Meier <pmeier82 at googlemail dot com>
# 2011-10-20
#

"""module for general data related plots"""
__docformat__ = 'restructuredtext'
__all__ = ['ModDataPlot']


##--- IMPORTS

import scipy as sp
from scipy.linalg import cholesky_banded
import spikeplot
from mdp import pca
from .base_module import BaseModule, ModuleInputError, ModuleExecutionError
from .result_types import MRPlot
from ..util import extract_spikes, dict_arrsort, dict_list2arr

spikeplot.mpl.interactive(False)


##---CLASSES

class ModDataPlot(BaseModule):
    """module for data plots"""

    RESULT_TYPES = [
        MRPlot, # waveforms by units
        MRPlot, # waveforms all spikes
        MRPlot, # cluster PC1/2
        MRPlot, # cluster PC3/4
        MRPlot, # cluster projection
        MRPlot] # spike train set

    def _check_raw_data(self, raw_data):
        if raw_data is None:
            raise ModuleInputError('raw_data: '
                                   'needs raw data!')
        if raw_data.ndim != 2:
            raise ModuleInputError('rawdata: '
                                   'ndim != 2')
        if raw_data.shape[0] < sum(self.parameters['cut']):
            raise ModuleInputError('raw_data: '
                                   'fewer samples than waveform length!')
        return raw_data

    def _check_sts_ev(self, sts_ev):
        if sts_ev is None:
            raise ModuleInputError('sts_ev: '
                                   'needs evaluation spike train set')
        dict_list2arr(sts_ev)
        dict_arrsort(sts_ev)
        return sts_ev

    def _check_parameters(self, parameters):
        return {
            'sampling_rate':parameters.get('sampling_rate', 32000.0),
            'cut':parameters.get('cut', (32, 32)),
            'name':parameters.get('name', 'noname'),
            'noise_cov':parameters.get('noise_cov', None)}

    def _apply(self):
        self._stage = 2
        cut = self.parameters['cut']
        spikes = {}
        for k, v in sorted(self.sts_ev.items()):
            train = v[(v > cut[0]) * (v < self.raw_data.shape[0] - cut[1])]
            if len(train) == 0:
                continue
            epochs = sp.vstack((
                train - cut[0],
                train + cut[1])).T
            spikes[k] = extract_spikes(self.raw_data, epochs)

        # produce plot results
        self.plot_waveforms(spikes)
        self.plot_clusters(spikes)
        self.plot_spike_trains()

    def plot_waveforms(self, spikes):
        """:spikeplot.waveforms: plots

        There will be one plot with waveforms per unit and one plot with all
        waveforms stacked.

        :type spikes: dict
        :param spikes: one set of waveforms per unit {k:[n,samples]}
        """

        # produce plots for all units ...
        self.result.append(spikeplot.waveforms(
            spikes,
            #            samples_per_second=self.parameters['sampling_rate'],
            tf=sum(self.parameters['cut']),
            plot_mean=True,
            plot_single_waveforms=True,
            plot_separate=True,
            title='waveforms by units',
            show=False,
            filename=None))

        # produce plots for all spikes ...
        self.result.append(spikeplot.waveforms(
            sp.vstack(spikes.values()),
            #            samples_per_second=self.parameters['sampling_rate'],
            tf=sum(self.parameters['cut']),
            plot_mean=False,
            plot_single_waveforms=True,
            plot_separate=False,
            title='waveforms all spikes',
            #colours=['gray'],
            show=False,
            filename=None))

    def plot_clusters(self, spikes, noise_cov=None):
        """:spikeplot.cluster: and :spikeplot.cluster_projection: plots

        There will be two plots visualizing the clustering and discrimination
        of the sorting. One showing the clustering of units (scatter plot
        using the first two principal components). The initial cluster
        labels are preserved as colorization in the projected data.

        Additionally there will be a plot showing the projection of each
        cluster coupling onto the vector connecting the corresponding cluster
        means/centers

        :type spikes: dict
        :param spikes: one set of waveforms per unit {k:[n,samples]}
        :type noise_cov: ndarray
        :param noise_cov: noise covariance matrix compatible with the
            dimension of individual observations in :spikes:
        """

        # prepare data
        tf = sum(self.parameters['cut'])
        # TODO: prewhiten
        data_stacked = pca(sp.vstack(spikes.values()), output_dim=4)
        data = {}
        idx = 0
        for k, v in spikes.items():
            n = v.shape[0]
            data[k] = data_stacked[idx:idx + n]
            idx += n

        # produce scatter plots
        for pcs in [(0, 1), (2, 3)]:
            self.result.append(spikeplot.cluster(
                data,
                data_dim=pcs,
                plot_mean=True,
                title='cluster plot',
                xlabel='PC%s' % (pcs[0] + 1),
                ylabel='PC%s' % (pcs[1] + 1),
                show=False,
                filename=None))

        # CLUSTER CENTER PROJECTIONS
        self.result.append(spikeplot.cluster_projection(
            data,
            show=False,
            filename=None))

    def plot_spike_trains(self):
        """:spikeplot.spike_train: plot

        There will be one plot for the spike train set.
        """

        self.result.append(spikeplot.spike_trains(
            self.sts_ev,
            samples_per_second=self.parameters['sampling_rate'],
            marker_width=1,
            show=False,
            filename=None))

##--- MAIN

if __name__ == '__main__':
    pass
