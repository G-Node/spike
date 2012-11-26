##---IMPORTS

import plot, util

from .models import ResultDefaultVisual
from ..base_module import BaseModule, ModuleInputError, ModuleExecutionError

from StringIO import StringIO
import scipy as sp

from django.core.files.uploadedfile import InMemoryUploadedFile

##---METRIC CONTEXT

class Module(BaseModule):
    """module implementation"""

    def _check_parameters(self, parameters):
        return {
            'sampling_rate': parameters.get('sampling_rate', 32000.0),
            'cut': parameters.get('cut', (32, 32)),
            'name': parameters.get('name', 'noname'),
            'noise_cov': parameters.get('noise_cov', None)}

    def _check_raw_data(self, raw_data):
        if raw_data is None:
            raise ModuleInputError('raw_data: needs raw data!')
        if raw_data.ndim != 2:
            raise ModuleInputError('raw_data: ndim != 2')
        if raw_data.shape[0] < sum(self.parameters['cut']):
            raise ModuleInputError('raw_data: fewer samples than waveform length!')
        return raw_data

    def _check_sts_ev(self, sts_ev):
        if sts_ev is None:
            raise ModuleInputError('sts_ev: needs evaluation spike train set')
        util.dict_list2arr(sts_ev)
        util.dict_arrsort(sts_ev)
        return sts_ev

    def _apply(self):
        cut = self.parameters['cut']
        spikes = {}
        for k, v in sorted(self.sts_ev.items()):
            train = v[(v > cut[0]) * (v < self.raw_data.shape[0] - cut[1])]
            if len(train) == 0:
                continue
            epochs = sp.vstack((
                train - cut[0],
                train + cut[1])).T
            spikes[k] = util.extract_spikes(self.raw_data, epochs)

        # produce plot results
        self.plot_waveforms(spikes)

    ## implementation

    def plot_waveforms(self, spikes):
        """:spikeplot.waveforms: plots

        There will be one plot with waveforms per unit and one plot with all
        waveforms stacked.

        :type spikes: dict
        :param spikes: one set of waveforms per unit {k:[n,samples]}
        """

        # produce plots for all units ...
        fig = plot.waveforms(
            spikes,
            #samples_per_second=self.parameters['sampling_rate'],
            tf=sum(self.parameters['cut']),
            plot_mean=True,
            plot_single_waveforms=True,
            plot_separate=True,
            title='waveforms by units')

        # save results
        #for i, t in enumerate(['wf_single', 'wf_all', 'clus12', 'clus34',
        #                       'clus_proj', 'spiketrain']):

    def create_result(self, ev):
        rval = ResultDefaultVisual(evaluation=ev, )
        rval.evaluation = ev
        # Create a file-like object to write image data created by PIL
        img_io = StringIO()
        modules[0].result[i].value.save(img_io, format='JPEG')
        # create a unique file name as: evaluation ID + picture prefix
        filename = "eval%d_%s.jpg" % (ev.id, t)
        # Create a new Django file-like object to be used in models as
        # ImageField using InMemoryUploadedFile.
        img_file = InMemoryUploadedFile(img_io, None, filename,
            'image/jpeg',
            img_io.len, None)
        rval.file = img_file
        rval.img_type = t
        rval.save()

##---MAIN

if __name__ == '__main__':
    pass
