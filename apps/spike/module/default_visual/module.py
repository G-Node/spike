##---IMPORTS

from spikeval.module import ModDefaultVisual, ModuleExecutionError

from .models import ResultDefaultVisual

from StringIO import StringIO

from django.core.files.uploadedfile import InMemoryUploadedFile

##---CONSTANTS

KINDS = dict(ResultDefaultVisual.KIND)

##---MODULE

class Module(ModDefaultVisual):
    """module for default visuals - for use in the django context"""

    #RESULT_TYPES = [
    # 10 'wf_single'    MRPlot, # waveforms by units
    # 20 'wf_all'       MRPlot, # waveforms all spikes
    # 30 'clus12'       MRPlot, # cluster PC1/2
    # 40 'clus34'       MRPlot, # cluster PC3/4
    # 50 'clus_proj'    MRPlot, # cluster projection
    # 60 'spiketrain'   MRPlot] # spike train set

    ## save django model results

    def save(self, mod, ev):
        """save django result entities"""

        # check for results
        if self._stage != 3:
            raise ModuleExecutionError('save initiated when module was not finalised!')

        # per result saving:
        for i, res in enumerate(self.result):
            # result
            kind = (i + 1) * 10
            rval = ResultDefaultVisual(evaluation=ev, module=mod, kind=kind)

            # data
            img_data = StringIO()
            res.value.save(img_data, format='PNG')

            # file
            filename = 'eval%d_%s.png' % (ev.id, KINDS.get(kind, 'unknown%d' % i))
            rval.file = InMemoryUploadedFile(
                file=img_data,
                field_name=None,
                name=filename,
                content_type='image/png',
                size=img_data.len,
                charset=None)
            rval.save()

##---MAIN

if __name__ == '__main__':
    pass
