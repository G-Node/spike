# SPIKESORTING EVALUATION WEBSITE - INSTALL INSTRUCTIONS

## 1. system level install

*do this as root*

These installs will need root or sudo permission. Some of the packages might
also be installed already. To install use:

    aptitude install <package-name>

#### package list

- git
- mysql-server-5.1
- rabbitmq-server
- python-virtualenv
- python-mysqldb
- python-numpy
- python-scipy
- python-matplotlib
- python-tables
- liblzo2-2
- python-imaging
- python-mdp

or in one command:

    aptitude install git mysql-server-5.1 rabbitmq-server python-virtualenv python-mysqldb python-numpy python-scipy python-matplotlib python-tables liblzo2-2 python-imaging python-mdp

mysql-server-5.1 will promt you to set the mysql root password,
liblzo2-2 is an unmet dependency for python-tables.

## 2. cloning the application sources

### 2.1 create directories
*do this as root*

    cd /opt
    mkdir spike
    chown www-data:www-data spike
    mkdir spike-env
    chown www-data:www-data spike-env

### 2.2 clone the sources
*do this as www-data*

We need a place to put the application sources. We will place the
application in /opt/spike. The apache2 will serve the website from here.

    cd /opt
    git clone git://github.com/G-Node/spike.git spike

### 2.3 create a virtual python environment
*do this as www-data*

create the virtualenv /opt/spike-env

in /opt do

    virtualenv spike-env
    source spike-env/bin/activate

(spike-env) should now appear infront of your shell primer

in /opt do

    pip install -r spike/deploy/requirements_pinax.txt
    pip install -r spike/deploy/requirements_spike_eval.txt
    pip install -r spike/deploy/requirements_celery.txt

This will populate the virutal python environment with the neccessary packages
using pip as the package manager.

## 3. django/pinax configuration

### 3.1 database setup
*do this as root*

    mysql -p

Chose a databse name and database user:password. We use spike:spike@spike
here.

in mysql console do

    CREATE DATABASE spike;
    USE spike;
    GRANT ALL PRIVILEGES ON spike.* TO spike@"%" IDENTIFIED BY "spike"

### 3.2 configure settings_locale.py
*do this as www-data*

change to /opt/spike

    mkdir log
    cp settings_local.temp.py settings_local.py

configure the entries

**DEBUG**: For setup and testing is suggest to to keep the DEBUG = TRUE. This
will provide detailed error messages over the web interface and serve the
static media from the template directories. COMPRESS will enable static file
compression (for css, js, etc).

**ADMINS**: Put an email in the ADMINS list and adjust the CONTANCT_EMAIL.
ADMINS will gen notified in case of errors, the CONTANCT_EMAIL is displayed
publicly on the frontend.

**DATABASES**: use the default database entry and adjust the login and host
entries as neccessary.

**LANGUAGE-AND-LOCALE**: (optional) adjust as neccessary

**FILES**: adjust the MEDIA_ROOT and STATIC_ROOT point to the absolute path
where static and user uploaded media files should be stored. Make sure this
has a trailing slash in the path, else the generated apache.conf will not
work.

**SECRET_KEY**: (optional) used for csrf-validation

**APPS**: add any additional django apps to INSTALLED_APPS and if they bring
middleware add those to MIDDLEWARE_CLASSES. Mind the += extension here.

**ACCOUNT**: (optional) account flags for account setup

**EMAIL**: configure the mx server you want to use

### 3.3 check the pinax/django environment
*do this as www-data*

    python manage.py shell

check that no import errors are thrown when importing e.g.
- pinax
- spikeval
- spike_eval

## 4. apache2 deployment

### 4.1 apache2 modules

you need apache2 with mod-wsgi installed

### 4.2 application deployment
*do this as www-data*

in /opt/spike call

    python deploy.py

validate generated the apache/apache.conf
validate generated wsgi.py

*do this as root*

create a link to the apache.conf in /etc/apache2/sites-available and
activate the page

    cd /etc/apache2/sites-available
    ln -s /opt/spike/apache/apache.conf spike
    a2ensite spike

!!!something is missing here!!!

in /etc/apache2/mods-available/wsgi.conf add

    WSGIPythonHome /opt/spike-env


# 5. miscellaneous settings

### 5.1 /etc/rc.local
*do this as root*

in /etc/rc.local add

    # for spike web site
    /etc/init.d/rabbitmq-server start
    echo -n 'Starting celeryd...'
    cd /opt/spike && /opt/spike-env/bin/python manage.py celeryd >& /var/log/celeryd.log &
    if [ $? -eq 0 ]; then
        echo " done."
    else
        echo " failed! Log in /var/log/celeryd.log!"
    fi


### 5.2 crontab for mail sending
*do this as root*

in /etc/cron.d/

    vim spike-mail

in that file enter these 2 lines:

    * * * * * www-data cd /opt/spike; (echo "----"; date ; /opt/spike-env/bin/python manage.py send_mail; date) >> /opt/spike/log/cron_mail.log 2>&1
    00,20,40 * * * * www-data cd /opt/spike; (echo "----"; date ; /opt/spike-env/bin/python manage.py retry_deferred; date) >> /opt/spike/log/cron_mail_deferred.log 2>&1
