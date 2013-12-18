#!/usr/bin/env python

## IMPORTS

import os, sys
from celery import Celery
from numpy.random import uniform

app = Celery('check', backend='amqp', broker='amqp://guest@localhost//')

## TASK

@app.task
def sample_task(n, min, max):
    rval = 0.0
    for i in xrange(n):
        rval += uniform(min, max, 1)
    return rval

## MAIN

if __name__ == "__main__":
    pass

## EOF
