##---IMPORTS

from django.dispatch import Signal

##---SIGNALS

sig_evaluation_run = Signal(providing_args=['pk'])
sig_validate_rd = Signal(providing_args=['pk'])
sig_validate_st = Signal(providing_args=['pk'])

##---MAIN

if __name__ == '__main__':
    pass
