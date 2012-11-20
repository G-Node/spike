##---IMPORTS

from django.dispatch import Signal

##---SIGNALS

spike_evaluation_run = Signal(providing_args=['pk'])
spike_validate_rd = Signal(providing_args=['pk'])
spike_validate_st = Signal(providing_args=['pk'])

##---MAIN

if __name__ == '__main__':
    pass
