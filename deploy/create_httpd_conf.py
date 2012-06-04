##---IMPORTS

import os

##---CONSTANTS

CONFIG_TEXT = """## apache config file for the spikesorting evaluation website
## generated by ./deploy/create_httpd_conf.py

<VirtualHost *:{svr_port}>

  # server and doc-root
  ServerName {svr_name}
  ServerAlias {svr_name}
  ServerAdmin {svr_email}
  DocumentRoot {dir_root}

  # media directories
  Alias /site_media {dir_media}
  <Directory {dir_media}>
    Order deny,allow
    Allow from all
  </Directory>

  # WSGI scripts
  WSGIDaemonProcess spike display-name=spike
  WSGIProcessGroup spike

  WSGIScriptAlias / {dir_root}/deploy/wsgi.py
  <Directory {dir_root}/deploy>
    Order deny,allow
    Allow from all
  </Directory>

</VirtualHost>

"""

##----FUNCTIONS

def create_apache_conf(
  svr_name='spike.g-node.org',
  svr_email='pmeier82@googlemail.com',
  svr_port='8001',
  dir_root='/opt/spike',
  dir_media='/data/spike_eval',
  ):
    if not os.path.exists('../apache'):
        os.mkdir('../apache')
    if not os.path.isdir('../apache'):
        raise IOError('../apache exists but is not a directory!')
    with open('../apache/apache.conf', 'w') as conf_file:
        conf_str = CONFIG_TEXT.format(
            svr_name=svr_name,
            svr_email=svr_email,
            svr_port=svr_port,
            dir_root=dir_root,
            dir_media=dir_media)
        conf_file.write(conf_str)

##---MAIN

if __name__ == '__main__':
    create_apache_conf()
