##---IMPORTS

import os
import pinax.env

##---ENVIRONMENT

pinax.env.setup_environ(__file__)

from django.conf import settings

##---CONSTANTS

CELERY_TEXT = ''
if getattr(settings, 'USE_CELERY'):
    CELERY_TEXT = 'os.environ["CELERY_LOADER"] = "django"'

AP_CFG_TEXT = """## apache config file for the spikesorting evaluation website
              ## generated by ./deploy/deploy_apache_wsgi.py

              <VirtualHost *:{svr_port}>

                # server and doc-root
                ServerName {svr_name}
                ServerAlias {svr_name}
                ServerAdmin {svr_email}
                DocumentRoot {PROJECT_ROOT}

                # logs
                ErrorLog {PROJECT_ROOT}/error.log
                customLog {PROJECT_ROOT}/access.log combined

                # directories
                Alias {MEDIA_URL} {MEDIA_ROOT}
                <Directory {MEDIA_ROOT}>
                  Order deny,allow
                  Allow from all
                </Directory>
                Alias {STATIC_URL} {STATIC_ROOT}
                <Directory {STATIC_ROOT}>
                  Order deny,allow
                  Allow from all
                </Directory>

                # wsgi script
                WSGIScriptAlias / {PROJECT_ROOT}/wsgi.py
                WSGIDaemonProcess spike display-name=spike user=spike
                group=spike home={PROJECT_ROOT}
                WSGIProcessGroup spike
                <Directory {PROJECT_ROOT}>
                  <Files wsgi.py>
                    Order deny, allow
                    Allow from all
                  </Files>
                </Directory>

              </VirtualHost>

              """

WSGI_PY_TEXT = """## wsgi handler for apache2
              ## generated by ./deploy/deploy_apache_wsgi.py

              from pinax.env import setup_environ
              from django.core.handlers.wsgi import WSGIHandler

              setup_environ(__file__)

              import os
              import sys
              sys.path.append("/opt/spike/")
              {CELERY_TEXT}

              application = WSGIHandler()

              """

##---FUNCTIONS

def create_apache_conf(
  svr_name='spike.g-node.org',
  svr_email='spike-admin@g-node.org',
  svr_port='8001'):
    root_dir = getattr(settings, 'PROJECT_ROOT')
    apache_dir = os.path.join(root_dir, 'apache')
    if not os.path.isdir(apache_dir):
        os.mkdir(apache_dir)
    with open(os.path.join(apache_dir, 'apache.conf'), 'w') as ap_cfg:
        ap_cfg.write(
            AP_CFG_TEXT.format(
                svr_name=svr_name,
                svr_email=svr_email,
                svr_port=svr_port,
                PROJECT_ROOT=getattr(settings, 'PROJECT_ROOT'),
                MEDIA_ROOT=getattr(settings, 'MEDIA_ROOT'),
                MEDIA_URL=getattr(settings, 'MEDIA_URL'),
                STATIC_ROOT=getattr(settings, 'STATIC_ROOT'),
                STATIC_URL=getattr(settings, 'STATIC_URL')))
    with open(os.path.join(root_dir, 'wsgi.py'), 'w') as wsgi_py:
        wsgi_py.write(WSGI_PY_TEXT.format(CELERY_TEXT=CELERY_TEXT))

##---MAIN

if __name__ == '__main__':
    create_apache_conf()
