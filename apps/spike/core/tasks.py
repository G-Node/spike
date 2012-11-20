##---IMPORTS

from django.db import models
from celery.task import task
from StringIO import StringIO
from spikeval.datafiles import read_gdf_sts, read_hdf5_arc
from spikeval.logging import Logger
import scipy as sp

##---MODEL-REFS

Data = models.get_model('spike', 'data')

##---HELPERS

def toint(val):
    #if type(val) == type(""):
    res = int(float(val))
    return res

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
def validate_rawdata_file(pk):
    """checks consistency of rawdata file

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
        assert df.file_type == 'rd_file'
        tr = df.content_object
    except:
        logger.log('ERROR')
        return valid

    try:
        logger.log('looking at raw data file with id: %s' % pk)
        rd, sr = read_hdf5_arc(df.file.path)
        logger.log('found rd_file: %s' % df.name)
        len_rd_sec = rd.shape[0] / sr
        logger.log('found data in %d channels, for %d sec' % (
            rd.shape[1], len_rd_sec))

        # TODO: more checks?

        logger.log('rd_file passed all checks')
        valid = True
    except Exception, ex:
        logger.log('ERROR: trial check: %s' % str(ex))
    finally:
        df.save()
        tr.valid_rd_log = logger.get_content()
        tr.save()
        return valid


@task
def validate_spiketrain_file(dfid):
    """checks consistency of ground truth file

    :type dfid: int
    :param dfid: pk for Data entity

    :returns: bool -- True if Data validates, False else. Processing
    log, including errors, will be written to the Data entity.
    """

    # init and checks
    valid = False
    logger = Logger.get_logger(StringIO())
    try:
        df = Data.objects.get(id=dfid)
        assert df.file_type == 'st_file'
        tr = df.content_object
    except:
        logger.log('ERROR')
        return valid

    try:
        logger.log('looking at ground truth file version with uid: %s' % df.id)
        gt = read_gdf_sts(df.file.path)
        logger.log('found gt_file: %s' % df.name)
        for st in gt:
            if not isinstance(gt[st], sp.ndarray):
                raise TypeError('spike train %s not ndarray' % st)
            if not gt[st].ndim == 1:
                raise ValueError('spike trains have to be ndim==1')

        # TODO: more checks?

        logger.log('gt_file passed all checks')
        valid = True
    except Exception, ex:
        logger.log('ERROR: trial check: %s' % str(ex))
    finally:
        df.save()
        tr.valid_gt_log = logger.get_content()
        tr.save()
        return valid

##---MAIN

if __name__ == '__main__':
    pass
