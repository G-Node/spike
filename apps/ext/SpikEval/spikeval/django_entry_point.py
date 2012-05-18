# -*- coding: utf-8 -*-
#
# spikeval - django_entry_point.py
#
# Philipp Meier - <pmeier82 at gmail dot com>
# 2011-10-14
#

"""django specific functions and entry point"""
__docformat__ = 'restructuredtext'
__all__ = ['check_record', 'start_eval']

##---IMPORTS

import sys
from StringIO import StringIO
from datetime import datetime
from .core import eval_core
from .datafiles import read_gdf_sts, read_hdf5_arc
from .logging import Logger
from .module import MODULES
import scipy as sp

# g-node imports
from django.core.files.uploadedfile import InMemoryUploadedFile
from benchmarks.models import Record
from evaluations.models import (Evaluation, EvaluationResults,
                                EvaluationResultsImg)

##---FUNCTIONS

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
#record = Record.get(id = key)
#
#gtfilepath = record.groundtruth.path
#rawfilepath = record.raw_data.path
#
#[then check the files ... (gtfilepath, rawfilepath)]
#
#record.verfied = boolean
#recrod.verified_error = "string"
#
#return

def check_record(key):
    """checks consistency of (raw_data, ground truth spike train) tuple

    :type key: int
    :param key: unique record identifier

    :returns: bool -- True if benchmark files comply, False else. Processing
    log, including errors, will be written to the Record object.
    """

    rec = Record.objects.get(id=key)

    # checking ground truth spike train file -- should be gdf
    logger = Logger.get_logger(StringIO())
    gt_v = rec.get_active_gfile().get_version()
    logger.log('looking at groundtruth file version with uid: %s' % gt_v.id)
    gt_valid = False
    try:
        gt = read_gdf_sts(gt_v.raw_file.path)
        logger.log('found gt_file: %s' % gt_v.title)
        for st in gt:
            if not isinstance(gt[st], sp.ndarray):
                raise TypeError('spike train %s not ndarray' % st)
            if not gt[st].ndim == 1:
                raise ValueError('spike trains have to be ndim==1')
        logger.log('gt_file passed all checks')

        # TODO: more checks?

        gt_v.validation_state = "S" # success
        gt_valid = True
    except Exception, ex:
        gt_valid = False
        gt_v.validation_state = "F" # indicates failure
        logger.log('error during record check: %s' % str(ex))
    gt_v.validation_log = logger.get_content()
    gt_v.save()

    # checking raw data file -- should be hdf5
    logger = Logger.get_logger(StringIO())
    rd_v = rec.get_active_rfile().get_version()
    logger.log('looking at raw data file version with uid: %s' % rd_v.id)
    rd_valid = False
    try:
        rd, sr = read_hdf5_arc(rd_v.raw_file.path)
        logger.log('found rd_file: %s' % rd_v.raw_file.path)
        len_rd_sec = rd.shape[0] / sr
        logger.log('found data in %d channels, for %d sec' % (
            rd.shape[1], len_rd_sec))

        # TODO: more checks?

        rd_v.validation_state = "S" # success
        rd_valid = True
    except Exception, ex:
        rd_valid = False
        rd_v.validation_state = "F" # indicates failure
        logger.log('error during record check: %s' % str(ex))
    rd_v.validation_log = logger.get_content()
    rd_v.save()

    # all checks passed
    return gt_valid and rd_valid

#+Interface 2: The user uploads a sorting result. The frontend calls a
#backend function and displays the state of the evaluation to the user.
#the backend instantiates an object with which to control that user
#output and return the log of the evaluation. This object will also
#store the evaluation results
#
#The function call gets the following inputs:
#1. path to upload file: str
#2. path to benchmark raw data file: str
#3. path to benchmark gt file: str
#4. key for this evaluation: int
#5. path to a temp directory: str
#
#The backend function does not return anything, all output will again
#be done by the Object e.g.
#import ResultsObject
#res = ResultsObject(id = key)
#
#res.log = "bla"
#res.image = Image
#...
def start_eval(path_rd, path_ev, path_gt, key, log=sys.stdout, **kwargs):
    """core function to produce one evaluation result based on one set of
    data, ground truth spike train and estimated spike train.

    :type path_rd: str
    :param path_rd: path to the file holding the raw data
    :type path_ev: str
    :param path_ev: path to the file holding the estimated spike train
    :type path_gt: str
    :param path_gt: path to the file holding the ground truth spike train
    :type key: int
    :param key: unique evaluation key
    :type log: file_like
    :param log: logging stream
        Default=sys.stdout
    :keyword ??: any, will be passed to modules as parameters

    :returns: None
    """

    # inits
    problems = False
    logger = Logger.get_logger(log)
    evaluation = Evaluation.objects.get(id=key)
    logger.log('processing evaluation ID %s' % key)

    # read in evaluation file
    logger.log('reading input files')
    rd, sampling_rate = read_hdf5_arc(path_rd)
    if sampling_rate is not None:
        kwargs.update(sampling_rate=sampling_rate)
    ev = read_gdf_sts(path_ev)
    gt = read_gdf_sts(path_gt)
    logger.log('done reading input files')

    # apply modules
    logger.log('starting evaluation loop:')
    modules = []
    for mod_cls in MODULES:
        try:
            logger.log('starting module: %s' % mod_cls.__name__)
            tick = datetime.now()
            this_mod = eval_core(rd, gt, ev, mod_cls, logger, **kwargs)
            tock = datetime.now()
            logger.log('finished: %s' % str(tock - tick))
        except Exception, ex:
            logger.log_delimiter_line()
            logger.log(str(ex))
            logger.log_delimiter_line()
            problems = True
        finally:
            modules.append(this_mod)
    logger.log('done evaluating')

    logger.log('starting to save evaluation results')
    # care for static result mapping of images,
    # we will send PIL Image instances here!
    if modules[0].status == 'finalised':
        for i, t in enumerate(['wf_single', 'wf_all', 'clus12', 'clus34',
                               'clus_proj', 'spiketrain']):
            rval = EvaluationResultsImg()
            rval.evaluation = evaluation
            # Create a file-like object to write image data created by PIL
            img_io = StringIO()
            modules[0].result[i].value.save(img_io, format='JPEG')
            # create a unique file name as: evaluation ID + picture prefix
            filename = "eval%d_%s.jpg" % (evaluation.id, t)
            # Create a new Django file-like object to be used in models as
            # ImageField using InMemoryUploadedFile.
            img_file = InMemoryUploadedFile(img_io, None, filename,
                                            'image/jpeg',
                                            img_io.len, None)
            rval.img_data = img_file
            rval.img_type = t
            rval.save()
    else:
        logger.log('problem with %s: not finalised!' %
                   modules[1].__class__.__name__)
        problems = True

    # care for static result mapping of alignment statistic,
    # we will send a MRTable instance here
    if modules[1].status == 'finalised':
        for row in modules[1].result[0].value:
            rval = EvaluationResults()
            rval.evaluation = evaluation
            rval.gt_unit = row[0]
            rval.found_unit = row[1]
            rval.KS = toint(row[2])
            rval.KSO = toint(row[3])
            rval.FS = toint(row[4])
            rval.TP = toint(row[5])
            rval.TPO = toint(row[6])#
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
        problems = True
    evaluation.evaluation_log = logger.get_content()
    evaluation.processing_state = 20 # Success
    evaluation.save()
    return True


def toint(val):
    #if type(val) == type(""):
    res = int(float(val))
    return res

##---MAIN

if __name__ == '__main__':
    pass
