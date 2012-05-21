##---IMPORTS

from spikeval.django_entry_point import start_eval, check_record
#from celery.decorators import task
from celery.task import task
from StringIO import StringIO

##---TASKS

## FROM benchmarks.tasks.py

@task
def validate_record(rec_id):
    """ This task validates the groundtruth - raw data benchmark file pair."""
    result = check_record(rec_id)
    return result

## FROM evaluations.tasks.py

@task
def evaluate(path_rd, path_ev, path_gt, key, log=None):
    """ This task runs the spike sorting evaluation."""

    if log is None:
        log = StringIO()
    result = start_eval(path_rd, path_ev, path_gt, key, log)
    return result

if __name__ == '__main__':
    pass
