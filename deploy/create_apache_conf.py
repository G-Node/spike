##---IMPORTS

import os
import shutil
import pinax.env

##---ENVIRONMENT

pinax.env.setup_environ(__file__)

from django.conf import settings

##---CONSTANTS

APACHE_CONF_TEXT = """## apache config file for the spikesorting evaluation
website
## generated by ./deploy/create_apache_conf.py

<VirtualHost *:{svr_port}>

  # server and doc-root
  ServerName {svr_name}
  ServerAlias {svr_name}
  ServerAdmin {svr_email}
  DocumentRoot {PROJECT_ROOT}

  # media directory
  Alias {MEDIA_URL} {MEDIA_ROOT}
  <Directory {MEDIA_ROOT}>
    Order deny,allow
    Allow from all
  </Directory>

  # static directory
  Alias {STATIC_URL} {STATIC_ROOT}
  <Directory {STATIC_ROOT}>
    Order deny,allow
    Allow from all
  </Directory>

  # WSGI scripts
  WSGIDaemonProcess spike display-name=spike
  WSGIProcessGroup spike
  WSGIScriptAlias / {PROJECT_ROOT}/wsgi.py
  <Directory {PROJECT_ROOT}>
    <Files wsgi.py>
      Order allow,deny
      Allow from all
    </Files>
  </Directory>

</VirtualHost>

"""

WSGI_PY_TEXT = """# WSGI handler for apache2

from django.core.handlers.wsgi import WSGIHandler
from pinax.env import setup_environ

setup_environ(__file__)
application = WSGIHandler()

"""

##---FUNCTIONS

def create_apache_conf(
  svr_name='spike.g-node.org',
  svr_email='pmeier82@googlemail.com',
  svr_port='8001'):
    root_dir = getattr(settings, 'PROJECT_ROOT')
    with open(os.path.join(root_dir, 'apache', 'apache.conf'), 'w') as ap_cfg:
        ap_cfg.write(
            APACHE_CONF_TEXT.format(
                svr_name=svr_name,
                svr_email=svr_email,
                svr_port=svr_port,
                PROJECT_ROOT=getattr(settings, 'PROJECT_ROOT'),
                MEDIA_ROOT=getattr(settings, 'MEDIA_ROOT'),
                MEDIA_URL=getattr(settings, 'MEDIA_URL'),
                STATIC_ROOT=getattr(settings, 'STATIC_ROOT'),
                STATIC_URL=getattr(settings, 'STATIC_URL')))
    with open(os.path.join(root_dir, 'wsgi.py'), 'w') as wsgi_py:
        wsgi_py.write(WSGI_PY_TEXT)

##---MAIN

if __name__ == '__main__':
    create_apache_conf()
