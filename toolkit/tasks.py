##---IMPORTS

from django.core.management import call_command
from hosttemplate.celery.task import task

##---TASKS

@task
def DjangoMailer_send_mail():
    call_command('send_mail', interactive=True)


@task
def DjangoMailer_retry_deferred():
    call_command('retry_deferred', interactive=True)

##---MAIN

if __name__ == '__main__':
    pass
