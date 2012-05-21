# common imports
from ext.SpikEval.spikeval.django_entry_point import check_record
from celery.decorators import task

@task
def validate_record(rec_id):
    """ This task validates the groundtruth - raw data benchmark file pair."""
    result = check_record(rec_id)
    return result
