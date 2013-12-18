from __future__ import absolute_import

## IMPORTS

import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NAME.settings')

app = Celery('NAME')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLES_APPS)

## TASK

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

## MAIN

if __name__ == "__main__":
    pass

## EOF
