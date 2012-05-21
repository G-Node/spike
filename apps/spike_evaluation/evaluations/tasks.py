# common imports
from ext.SpikEval.spikeval.django_entry_point import start_eval
from celery.decorators import task

@task
def evaluate(path_rd, path_ev, path_gt, key, log):
    """ This task runs the spike sorting evaluation."""
    result = start_eval(path_rd, path_ev, path_gt, key, log)
    return result
