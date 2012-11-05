##---IMPORTS

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from .signals import sig_validate_st, sig_validate_rd
from .tasks import validate_rawdata_file as val_rd, validate_spiketrain_file as val_st

##---CONSTANTS

USE_CELERY = getattr(settings, 'USE_CELERY', False)

##---SIGNAL-CALLBACKS

@receiver(sig_validate_rd)
def validate_rawdata_file(sender, **kwargs):
    print 'signal caught:', sender
    if USE_CELERY:
        val_rd.delay(sender.rd_file.id)
    else:
        val_rd(sender.rd_file.id)


@receiver(sig_validate_st)
def validate_spiketrain_file(sender, **kwargs):
    print 'signal caught:', sender
    if USE_CELERY:
        val_st.delay(sender.st_file.id)
    else:
        val_st(sender.st_file.id)

##---MAIN

if __name__ == '__main__':
    pass