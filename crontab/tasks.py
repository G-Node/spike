##---IMPORTS

from django.conf import settings
from django.core.management import call_command
from celery.task import task

##---TASKS

@task
def DjangoMailer_send_mail():
    print 'call django-mailer send_mail'


@task
def DjangoMailer_retry_deferred():
    print 'call django-mailer retry_deferred'

##---MAIN

if __name__ == '__main__':
    pass
