##---IMPORTS

from django.conf import settings
from django.db import models
from django.utils import importlib
from celery.task import task
from datetime import datetime
from StringIO import StringIO
from spikeval.datafiles import read_gdf_sts, read_hdf5_arc
from spikeval.logging import Logger

from ..signals import spike_evaluation_run

##---MODEL-REFS

Evaluation = models.get_model('spike', 'evaluation')
Module = models.get_model('spike', 'module')

##---CELERY-USAGE

USE_CELERY = getattr(settings, 'USE_CELERY', False)
if getattr(settings, 'CELERY_USE_PRIORITY', None) is not None:
    USE_CELERY = getattr(settings, 'CELERY_USE_PRIORITY')

##---RECEIVER

def run_modules_for_evaluation(sender, **kwargs):
    # DEBUG
    print 'starting evaluation [class: %s::%s]' % (sender.__class__.__name__, sender.id)
    # BUGED

    if USE_CELERY:
        task_run_modules.delay(sender)
    else:
        task_run_modules(sender)

spike_evaluation_run.connect(run_modules_for_evaluation, dispatch_uid=__file__)
#spike_evaluation_run.connect(run_modules_for_evaluation, sender=Evaluation, dispatch_uid=__file__)

##---TASKS

@task
def task_run_modules(ev, **kwargs):
    """core function to run all modules for an evaluation

    :type ev: Evaluation
    :param ev: Evaluation entity
    :keyword: any, will be passed to modules as parameters

    :returns: True on success, False on error
    """

    success = None
    try:
        ev.status = ev.STATUS.running
        ev.save()
        mod_list = ev.trial.benchmark.module_set.all()
        logger = Logger.get_logger(StringIO())
    except:
        success = False
    else:
        try:
            logger.log_delimiter_line()

            rd_file = ev.trial.rd_file
            gt_file = ev.trial.gt_file
            ev_file = ev.ev_file
            logger.log('processing: %s' % ev)

            logger.log('reading input files')
            rd, sampling_rate = read_hdf5_arc(rd_file.file.path)
            if sampling_rate is not None:
                kwargs.update(sampling_rate=sampling_rate)
            ev_sts = read_gdf_sts(ev_file.file.path)
            gt_sts = read_gdf_sts(gt_file.file.path)
            logger.log('done reading input files')

            logger.log_delimiter_line()

            # modules
            assert len(mod_list), 'Module list is empty!'
            for mod in mod_list:
                logger.log('starting module: %s' % mod)
                module_pkg = importlib.import_module('spike.module.%s' % mod.path)
                _tick_ = datetime.now()
                module = module_pkg.module_cls(rd, gt_sts, ev_sts, logger, **kwargs)
                module.apply()
                module.save(mod, ev)
                _tock_ = datetime.now()
                logger.log('finished: %s' % str(_tock_ - _tick_))
                logger.log_delimiter_line()
                del module, module_pkg
        except Exception, ex:
            logger.log('ERROR: (%s) %s' % (ex.__class__.__name__, str(ex)))
            success = False
            ev.status = ev.STATUS.failure
        else:
            success = True
            ev.status = ev.STATUS.success
        finally:
            ev.task_log = logger.get_content()
            ev.save()
            print ev.task_log
    finally:
        return success

##---MAIN

if __name__ == '__main__':
    pass
