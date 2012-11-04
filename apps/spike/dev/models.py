##---IMPORTS

from django.contrib import messages
from django.db import models
from django.shortcuts import redirect
from django.dispatch import receiver
from ..core.signals import sig_validate_rd
from ..util import render_to

##---VIEWS

#@receiver(sig_validate_rd)
def signal_test(sender, **kwargs):
    print 'evaluation_run received:', sender, kwargs

##---MAIN

if __name__ == '__main__':
    pass
