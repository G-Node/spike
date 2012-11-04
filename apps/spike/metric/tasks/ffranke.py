##---IMPORTS

from django.conf import settings
from django.db import models
from celery.task import task
from StringIO import StringIO
from datetime import datetime
from spikeval.core import eval_core
from spikeval.datafiles import read_gdf_sts, read_hdf5_arc
from spikeval.logging import Logger
from spikeval.module import ModMetricAlignment

__all__ = ['metric_ffranke']

##---MODEL-REFS

Evaluation = models.get_model('spike', 'evaluation')
EvaluationResult = models.get_model('spike', 'evaluationresult')
Metric = models.get_model('spike', 'metric')
spike = models.get_app('spike')

##---CONSTANTS

USE_CELERY = getattr(settings, 'USE_CELERY', False)

##---HELPERS

def toint(val):
    #if type(val) == type(""):
    res = int(float(val))
    return res

TEST_METRIC = Metric.objects.get(pk=1)

##---TASKS

@task
def metric_ffranke(pk, **kwargs):
    """core function to produce one evaluation result based on one set of
    data, ground truth spike train and estimated spike train.
    :type pk: int
    :param pk: pk for Evaluation entity
    :type log: file_like
    :param log: logging stream
        Default=sys.stdout
    :keywords: any, will be passed to modules as parameters

    :returns: None
    """

    # init and checks
    valid = False
    try:
        ev = Evaluation.objects.get(id=pk)
        logger = Logger.get_logger(StringIO())
        EvaluationResult = models.get_model('spike', 'evaluationresult')
    except:
        return valid

    try:
        rd_file = ev.trial.rd_file
        gt_file = ev.trial.gt_file
        ev_file = ev.ev_file
        logger.log('processing evaluation ID: %s' % pk)

        # read in evaluation file
        logger.log('reading input files')
        rd, sampling_rate = read_hdf5_arc(rd_file.file.path)
        if sampling_rate is not None:
            kwargs.update(sampling_rate=sampling_rate)
        ev_sts = read_gdf_sts(ev_file.file.path)
        gt_sts = read_gdf_sts(gt_file.file.path)
        logger.log('done reading input files')

        # apply modules
        logger.log('starting evaluation:')
        try:
            logger.log('starting module: %s' % ModMetricAlignment.__class__.__name__)
            tick = datetime.now()
            this_mod = eval_core(rd, gt_sts, ev_sts, ModMetricAlignment, logger, **kwargs)
            tock = datetime.now()
            logger.log('finished: %s' % str(tock - tick))
        except Exception, ex:
            logger.log_delimiter_line()
            logger.log(str(ex))
            logger.log_delimiter_line()
            this_mod = None
        logger.log('done evaluating')

        logger.log('starting to save evaluation results')
        if this_mod.status == 'finalised':
            for row in this_mod.result[0].value:
                rval = EvaluationResult(metric=TEST_METRIC)
                rval.evaluation = ev
                rval.gt_unit = row[0]
                rval.found_unit = row[1]
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
            logger.log('done saving results')
        else:
            logger.log('problem with %s: not finalised!' % this_mod.__class__.__name__)
        valid = True
    except Exception, ex:
        logger.log('ERROR: %s' % str(ex))
        valid = False
    finally:
        ev.task_state = valid
        ev.task_log += '\n\n' + logger.get_content()
        ev.save()
        print ev.task_log
        return valid

##---MAIN

if __name__ == '__main__':
    pass
