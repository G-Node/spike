##---IMPORTS

from django.conf import settings
from django.db import models
from celery.task import task
from StringIO import StringIO
from datetime import datetime
from spikeval.core import eval_core
from spikeval.datafiles import read_gdf_sts, read_hdf5_arc
from spikeval.logging import Logger
from spikeval.module import MODULES
import scipy as sp

from django.core.files.uploadedfile import InMemoryUploadedFile

##---MODEL-REFS

Datafile = models.get_model('spike', 'datafile')
Evaluation = models.get_model('spike', 'evaluation')
EvaluationResult = models.get_model('spike', 'evaluationresult')
EvaluationResultImg = models.get_model('spike', 'evaluationresultimg')

##---CONSTANTS

USE_CELERY = getattr(settings, 'USE_CELERY', False)

##---HELPERS

def toint(val):
    #if type(val) == type(""):
    res = int(float(val))
    return res

##---TASKS

@task
def _start_evaluation(evid, **kwargs):
    """core function to produce one evaluation result based on one set of
    data, ground truth spike train and estimated spike train.
    :type evid: int
    :param evid: pk for Evaluation entity
    :type log: file_like
    :param log: logging stream
        Default=sys.stdout
    :keywords: any, will be passed to modules as parameters

    :returns: None
    """

    # init and checks
    state = 30
    try:
        ev = Evaluation.objects.get(id=evid)
        logger = Logger.get_logger(StringIO())
    except:
        return state

    try:
        rd_file = ev.trial.rd_file
        gt_file = ev.trial.gt_file
        ev_file = ev.ev_file
        logger.log('processing evaluation ID: %s' % evid)

        # read in evaluation file
        logger.log('reading input files')
        rd, sampling_rate = read_hdf5_arc(rd_file.file.path)
        if sampling_rate is not None:
            kwargs.update(sampling_rate=sampling_rate)
        ev_sts = read_gdf_sts(ev_file.file.path)
        gt_sts = read_gdf_sts(gt_file.file.path)
        logger.log('done reading input files')

        # apply modules
        logger.log('starting evaluation loop:')
        modules = []
        for mod_cls in MODULES:
            try:
                logger.log('starting module: %s' % mod_cls.__name__)
                tick = datetime.now()
                this_mod = eval_core(rd, gt_sts, ev_sts, mod_cls, logger, **kwargs)
                tock = datetime.now()
                logger.log('finished: %s' % str(tock - tick))
            except Exception, ex:
                logger.log_delimiter_line()
                logger.log(str(ex))
                logger.log_delimiter_line()
                this_mod = None
            finally:
                modules.append(this_mod)
        logger.log('done evaluating')

        logger.log('starting to save evaluation results')
        # care for static result mapping of images,
        # we will send PIL Image instances here!
        if modules[0].status == 'finalised':
            for i, t in enumerate(['wf_single', 'wf_all', 'clus12', 'clus34',
                                   'clus_proj', 'spiketrain']):
                rval = EvaluationResultImg()
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
        else:
            logger.log('problem with %s: not finalised!' %
                       modules[1].__class__.__name__)

        # care for static result mapping of alignment statistic,
        # we will send a MRTable instance here
        if modules[1].status == 'finalised':
            for row in modules[1].result[0].value:
                rval = EvaluationResult()
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
            logger.log('problem with %s: not finalised!' %
                       modules[1].__class__.__name__)
        state = 20 # Success
    except Exception, ex:
        logger.log('Exception: %s' % str(ex))
        state = 30 # Failure
    finally:
        ev.task_state = state
        ev.task_log = logger.get_content()
        ev.save()
        print ev.task_log
        return state


def start_evaluation(evid):
    rval = 0
    if USE_CELERY:
        rval = _start_evaluation.delay(evid)
    else:
        _start_evaluation(evid)
    return str(rval)

##---MAIN

if __name__ == '__main__':
    pass
