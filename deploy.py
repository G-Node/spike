#!/usr/bin/env python

##---IMPORTS

import os, sys
import argparse
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spike_g_node_org.settings")

from django.conf import settings

##---RABBITMQ-CONF

RABBITMQ_CONF = """
# ========================================
#  rabbitmq supervisor conf
# ========================================
# generated by deploy.py - {DATE}

[program:rabbitmq]
command=/usr/sbin/rabbitmq-server
priority=1001

"""

def create_rabbitmq_conf():
    print 'starting rabbitmq.conf'
    conf_path = os.path.join(getattr(settings, 'PROJECT_ROOT'), 'deploy', 'rabbitmq.conf')
    if os.path.exists(conf_path):
        print 'removing old rabbitmq.conf .. ',
        os.remove(conf_path)
        print 'done'
    with open(conf_path, 'w') as cfg_file:
        cfg_file.write(RABBITMQ_CONF.format(DATE=datetime.datetime.now()))
    print 'done with rabbitmq.conf'
    print
    return 0

##---APPACHE_CONF

APACHE_CONF = """
# ==================================
#  apache conf for Django with WSGI
# ==================================
# for django instance: {SVR_NAME}
# generated by deploy.py - {DATE}

Listen {SVR_PORT}
NameVirtualHost *:{SVR_PORT}

WSGIPythonHome {PYTHON_HOME}

<VirtualHost *:{SVR_PORT}>

  # server and doc-root
  ServerName {SVR_NAME}
  ServerAlias {SVR_NAME}
  ServerAdmin {SVR_EMAIL}
  DocumentRoot {PROJECT_ROOT}

  # logs
  ErrorLog {PROJECT_ROOT}/log/error.log
  CustomLog {PROJECT_ROOT}/log/access.log combined

  # directories
  Alias {MEDIA_URL} {MEDIA_ROOT}/
  <Directory {MEDIA_ROOT}/>
    Order deny,allow
    Allow from all
  </Directory>
  Alias {STATIC_URL} {STATIC_ROOT}/
  <Directory {STATIC_ROOT}/>
    Order deny,allow
    Allow from all
  </Directory>

  # wsgi script
  WSGIScriptAlias / {PACKAGE_ROOT}/wsgi.py
  WSGIDaemonProcess {WSGI_NAME} display-name={WSGI_NAME} home={PROJECT_ROOT} processes=1 threads=10 maximum-requests=32 inactivity-timeout=300
  WSGIProcessGroup {WSGI_NAME}
  <Directory {PACKAGE_ROOT}>
    <Files wsgi.py>
      Order allow,deny
      Allow from all
    </Files>
  </Directory>

</VirtualHost>

"""

def create_apache_conf():
    print 'starting apache.conf'
    conf_path = os.path.join(getattr(settings, 'PROJECT_ROOT'), 'deploy', 'apache.conf')
    if os.path.exists(conf_path):
        print 'removing old apache.conf .. ',
        os.remove(conf_path)
        print 'done'
    print 'Please provide some information:'
    svr_name = raw_input('server name [spike.g-node.org]:') or 'spike.g-node.org'
    svr_email = raw_input('server email [noname@%s]:' % svr_name) or 'noname@%s' % svr_name
    svr_port = int(raw_input('server port [80]:') or '80')
    wsgi_name = raw_input('process identifier [spike]:') or 'spike'
    python_home = raw_input('python home path [/opt/spike-env]') or '/opt/spike-env'
    with open(conf_path, 'w') as cfg_file:
        cfg_file.write(
            APACHE_CONF.format(
                SVR_NAME=svr_name,
                SVR_EMAIL=svr_email,
                SVR_PORT=svr_port,
                WSGI_NAME=wsgi_name,
                PYTHON_HOME=python_home,
                PACKAGE_ROOT=getattr(settings, 'PACKAGE_ROOT'),
                PROJECT_ROOT=getattr(settings, 'PROJECT_ROOT'),
                MEDIA_ROOT=getattr(settings, 'MEDIA_ROOT'),
                MEDIA_URL=getattr(settings, 'MEDIA_URL'),
                STATIC_ROOT=getattr(settings, 'STATIC_ROOT'),
                STATIC_URL=getattr(settings, 'STATIC_URL'),
                DATE=datetime.datetime.now()))
    print 'done with apache.conf'
    print
    return 0

##---CELERY-BEAT-CONF

CELERY_BEAT_CONF = """
# ========================================
#  celery beat supervisor conf for Django
# ========================================

[program:celery_beat]
command={PROJECT_ROOT}/manage.py celery beat --loglevel=INFO --events
directory={PROJECT_ROOT}
environment=PATH="{PYTHON_HOME}"
user=www-data
numprocs=1
stdout_logfile={PROJECT_ROOT}/log/celery_beat.log
stderr_logfile={PROJECT_ROOT}/log/celery_beat.log
autostart=true
autorestart=true
startsecs=10

# rabbitmq @ 1001, set its priority lower
priority=1002
"""

def create_celery_beat_conf():
    print 'starting celery_beat.conf'
    conf_path = os.path.join(getattr(settings, 'PROJECT_ROOT'), 'deploy', 'celery_beat.conf')
    if os.path.exists(conf_path):
        print 'removing old celery_beat.conf .. ',
        os.remove(conf_path)
        print 'done'
    print 'Please provide some information:'
    svr_name = raw_input('server name [spike.g-node.org]:') or 'spike.g-node.org'
    python_home = raw_input('python home path [/opt/spike-env]') or '/opt/spike-env'
    with open(conf_path, 'w') as cfg_file:
        cfg_file.write(
            CELERY_WORKER_CONF.format(
                SVR_NAME=svr_name,
                PYTHON_HOME=python_home,
                PROJECT_ROOT=getattr(settings, 'PROJECT_ROOT'),
                DATE=datetime.datetime.now()))
    print 'done with celery_beat.conf'
    print
    return 0

##---CELERY-WORKER-CONF

CELERY_WORKER_CONF = """
# ==========================================
#  celery worker supervisor conf for Django
# ==========================================
# for django instance: {SVR_NAME}
# generated by deploy.py - {DATE}

[program:celery_worker]
command={PROJECT_ROOT}/manage.py celery worker --loglevel=INFO --events
directory={PROJECT_ROOT}
environment=PATH="{PYTHON_HOME}"
user=www-data
numprocs=1
stdout_logfile={PROJECT_ROOT}/log/celery_worker.log
stderr_logfile={PROJECT_ROOT}/log/celery_worker.log
autostart=true
autorestart=true
startsecs=10

# Need to wait for currently executing tasks to finish at shutdown.
# Increase this if you have very long running tasks.
stopwaitsecs = 600

# rabbitmq @ 1001, set this priority higher!
priority=1002

"""

def create_celery_worker_conf():
    print 'starting celery_worker.conf'
    conf_path = os.path.join(getattr(settings, 'PROJECT_ROOT'), 'deploy', 'celery_worker.conf')
    if os.path.exists(conf_path):
        print 'removing old celery_worker.conf .. ',
        os.remove(conf_path)
        print 'done'
    print 'Please provide some information:'
    svr_name = raw_input('server name [spike.g-node.org]:') or 'spike.g-node.org'
    python_home = raw_input('python home path [/opt/spike-env]') or '/opt/spike-env'
    with open(conf_path, 'w') as cfg_file:
        cfg_file.write(
            CELERY_WORKER_CONF.format(
                SVR_NAME=svr_name,
                PYTHON_HOME=python_home,
                PROJECT_ROOT=getattr(settings, 'PROJECT_ROOT'),
                DATE=datetime.datetime.now()))
    print 'done with celery_worker.conf'
    print
    return 0

##---MAIN

if __name__ == '__main__':
    # argparse
    parser = argparse.ArgumentParser(description='Deployment Script.')
    parser.add_argument('task', type=str)
    task = vars(parser.parse_args())['task']

    # call
    assert task in ['all', 'rabbitmq', 'apache', 'celery_beat', 'celery_worker']

    def all_tasks():
        create_apache_conf()
        create_celery_beat_conf()
        create_celery_worker_conf()
        create_rabbitmq_conf()

    sys.exit(
        {'apache': create_apache_conf,
         'celery_beat': create_celery_beat_conf,
         'celery_worker': create_celery_worker_conf,
         'rabbitmq': create_rabbitmq_conf,
         'all': all_tasks
        }[task]()
    )
