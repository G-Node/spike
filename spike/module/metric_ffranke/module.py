##---IMPORTS

from spikeval.module import ModMetricFranke, ModuleExecutionError
from .models import ResultMetricFFranke

##---HELPERS

def toint(val):
    #if type(val) == type(""):
    res = int(float(val))
    return res

##---MODULE

class Module(ModMetricFranke):
    """module for the ffranke spikesorting metric - for use in the django context"""

    #RESULT_TYPES = [
    #    MRTable, # res_table - this is what we will save!
    #    MRTable, # similarity_matrix
    #    MRTable, # shift_matrix
    #    MRTable, # sp.atleast_2d(delta_shift)
    #    MRDict, # alignment
    #    MRDict, # O
    #    MRTable, # spike_no_assignment_matrix
    #    MRDict, # EL
    #    MRDict, # GL
    #    MRTable, # sp.atleast_2d(TP)
    #    MRTable, # sp.atleast_2d(TPO)
    #    MRTable, # sp.atleast_2d(FPA)
    #    MRTable, # sp.atleast_2d(FPAO)
    #    MRTable, # sp.atleast_2d(FN)
    #    MRTable, # sp.atleast_2d(FNO)
    #    MRTable, # sp.atleast_2d(FP)
    #    MRTable, # sp.atleast_2d(u_k2f)
    #    MRTable, # sp.atleast_2d(u_f2k)
    #]

    ## save django model results

    def save(self, mod, ev):
        """save django result entities"""

        # check for results
        if self._stage != 3:
            raise ModuleExecutionError('save initiated when module was not finalised!')

        # result saving
        for row in self.result[0].value:
            rval = ResultMetricFFranke(evaluation=ev, module=mod)
            rval.unit_gt = row[0]
            rval.unit_ev = row[1]
            rval.KS = toint(row[2])
            rval.KSO = toint(row[3])
            rval.FS = toint(row[4])
            rval.TP = toint(row[5])
            rval.TPO = toint(row[6])
            rval.FPA = toint(row[7])
            rval.FPAE = toint(row[8])
            rval.FPAO = toint(row[9])
            rval.FPAOE = toint(row[10])
            rval.FN = toint(row[11])
            rval.FNO = toint(row[12])
            rval.FP = toint(row[13])
            rval.save()

##---MAIN

if __name__ == '__main__':
    pass
