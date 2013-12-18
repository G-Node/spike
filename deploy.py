#!/usr/bin/env python

##---IMPORTS

import os, sys
import argparse
import datetime

# change this to the settings folder you want to use!
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "host_localhost.settings")

from django.conf import settings

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
  CustomLog {PROJECT_ROOT}/log/access.log combined
  ErrorLog {PROJECT_ROOT}/log/error.log

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
  WSGIDaemonProcess {WSGI_NAME} display-name={WSGI_NAME} home={PROJECT_ROOT} threads=16 maximum-requests=128 inactivity-timeout=300
  WSGIProcessGroup {WSGI_NAME}
  WSGIScriptAlias / {PACKAGE_ROOT}/wsgi.py
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
    python_home = raw_input('python home [%s]:' % sys.exec_prefix) or sys.exec_prefix
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

##---SUPERVISOR-CELERY-CONF

SUPERVISOR_CELERY_CONF = """
; ===================================
;  celery supervisor conf for Django
; ===================================
; for django instance: {SVR_NAME}
; generated by deploy.py - {DATE}

[program:celery_worker_{NAME}]
command={PYTHON} {PROJECT_ROOT}/manage.py celery worker -l INFO -E
directory={PROJECT_ROOT}
user=www-data
numprocs=1
stdout_logfile={PROJECT_ROOT}/log/celery_worker.log
stderr_logfile={PROJECT_ROOT}/log/celery_worker.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600

[program:celery_beat_{NAME}]
command={PYTHON} {PROJECT_ROOT}/manage.py celery beat -l INFO
directory={PROJECT_ROOT}
user=www-data
numprocs=1
stdout_logfile={PROJECT_ROOT}/log/celery_beat.log
stderr_logfile={PROJECT_ROOT}/log/celery_beat.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600

[group:celery_{NAME}]
programms: celery_worker_{NAME}, celery_beat_{NAME}

"""

def create_celery_conf():
    print 'starting celery.conf'
    conf_path = os.path.join(getattr(settings, 'PROJECT_ROOT'), 'deploy', 'celery.conf')
    if os.path.exists(conf_path):
        print 'removing old celery.conf .. ',
        os.remove(conf_path)
        print 'done'
    print 'Please provide some information:'
    svr_name = raw_input('server name [spike.g-node.org]:') or 'spike.g-node.org'
    proc_name = raw_input('process name [spike]:') or 'spike'
    python_exe = raw_input('python executable path [%s]' % sys.executable) or sys.executable
    with open(conf_path, 'w') as cfg_file:
        cfg_file.write(
            SUPERVISOR_CELERY_CONF.format(
                SVR_NAME=svr_name,
                NAME=proc_name,
                PYTHON=python_exe,
                PROJECT_ROOT=getattr(settings, 'PROJECT_ROOT'),
                DATE=datetime.datetime.now()))
    print 'done with celery.conf'
    print
    return 0

##---MAIN

if __name__ == '__main__':
    # argparse
    parser = argparse.ArgumentParser(description='Deployment Script.')
    parser.add_argument('task', type=str)
    task = vars(parser.parse_args())['task']

    # call
    assert task in ['all', 'apache', 'celery']

    def all_tasks():
        create_apache_conf()
        create_celery_conf()

    sys.exit(
        {'apache': create_apache_conf,
         'celery': create_celery_conf,
         'all': all_tasks
        }[task]()
    )