##---IMPORTS

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from celery.task import task
from StringIO import StringIO
from spikeval.datafiles import read_gdf_sts, read_hdf5_arc
from spikeval.logging import Logger
import scipy as sp
from .signals import spike_validate_st, spike_validate_rd
from ..log.models import Log

##---OVERRIDE-CELERY-FLAG

# DEBUG --- set to True or False to override settings, or None for no effect
CELERY_USE_PRIORITY = False
# BUGED

##---MODEL-REFS

Data = models.get_model('spike', 'data')

##---RECEIVERS

@receiver(spike_validate_rd)
def validate_rawdata_file(sender, **kwargs):
    # DEBUG
    print 'validate rawdata file:', sender
    # BUGED

    use_celery = getattr(settings, 'USE_CELERY', False)
    if CELERY_USE_PRIORITY is not None:
        use_celery = CELERY_USE_PRIORITY
    if use_celery:
        task_validate_rawdata_file.delay(sender.rd_file.id)
    else:
        task_validate_rawdata_file(sender.rd_file.id)


@receiver(spike_validate_st)
def validate_spiketrain_file(sender, **kwargs):
    # DEBUG
    print 'validate spiketrain file:', sender
    # BUGED

    use_celery = getattr(settings, 'USE_CELERY', False)
    if CELERY_USE_PRIORITY is not None:
        use_celery = CELERY_USE_PRIORITY
    if use_celery:
        task_validate_spiketrain_file.delay(sender.gt_file.id)
    else:
        task_validate_spiketrain_file(sender.gt_file.id)

##---TASKS

#+Interface 1: The user uploads a file pair. The frontend calls a
#backend function with the following inputs:
#int Key - identifier for the benchmark upload
#
#the backend will use the key to instantiate an object with which it
#can access the uploaded files. The files will be opened and checked
#for the content and return a boolean if the check was successful and a
#string containing information about the check like errors.
#
#This check function could look like:
#
#function checkBenchmark(key)
#import Record
#trial = Record.get(id = key)
#
#gtfilepath = trial.groundtruth.path
#rawfilepath = trial.raw_data.path
#
#[then check the files ... (gtfilepath, rawfilepath)]
#
#trial.verfied = boolean
#recrod.verified_error = "string"
#
#return

@task
def task_validate_rawdata_file(pk):
    """validates a rawdata file - that is an archive holding data to be analysed

    :type pk: int
    :param pk: pk for Data entity

    :returns: bool -- True if Data validates, False else. Processing
    log, including errors, will be written to the Data entity.
    """

    # init and checks
    valid = False
    logger = Logger.get_logger(StringIO())
    try:
        df = Data.objects.get(id=pk)
        assert df.kind == 'rd_file'
        tr = df.content_object
    except:
        logger.log('ERROR')
        return valid

    try:
        logger.log('looking at raw data file with pk: %s' % pk)
        rd, sr = read_hdf5_arc(df.file.path)
        logger.log('found rd_file: %s' % df.name)
        len_rd_sec = rd.shape[0] / sr
        logger.log('found data in %d channels, for %d sec' % (
            rd.shape[1], len_rd_sec))

        # TODO: more checks?

        logger.log('rd_file passed all checks')
        valid = True
    except Exception, ex:
        logger.log('ERROR: rawdata file check: %s' % str(ex))
    finally:
        df.save()
        tr.valid_rd_log = logger.get_content()
        tr.save()
        return valid


@task
def task_validate_spiketrain_file(pk):
    """validate a spiketrain file - that is a text file in gdf format (space separated, 2col, [key,time])

    :type pk: int
    :param pk: pk for Data entity

    :returns: bool -- True if Data validates, False else. Processing
    log, including errors, will be written to the Data entity.
    """

    # init and checks
    valid = False
    logger = Logger.get_logger(StringIO())
    try:
        df = Data.objects.get(id=pk)
        assert df.kind == 'st_file'
        tr = df.content_object
    except:
        logger.log('ERROR')
        return valid

    try:
        logger.log('looking at spiketrain file version with pk: %s' % df.id)
        sts = read_gdf_sts(df.file.path)
        logger.log('found st_file: %s' % df.name)
        for st in sts:
            if not isinstance(sts[st], sp.ndarray):
                raise TypeError('spike train %s not ndarray' % st)
            if not sts[st].ndim == 1:
                raise ValueError('spike trains have to be ndim==1')

        # TODO: more checks?

        logger.log('st_file passed all checks')
        valid = True
    except Exception, ex:
        logger.log('ERROR: spiketrain file check: %s' % str(ex))
    finally:
        df.save()
        tr.valid_gt_log = logger.get_content()
        tr.save()
        return valid

##---MAIN

if __name__ == '__main__':
    pass
