

# 1. system level install

*do this as root*

These installs will need root or sudo permission. Some of the packages might
also be installed already install by:

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
- python-imaging
- liblzo2-2
- python-mdp

or in one command:

    aptitude install git mysql-server-5.1 rabbitmq-server python-virtualenv python-mysqldb python-numpy python-scipy python-matplotlib python-tables python-imaging liblzo2-2 python-mdp

mysql-server-5.1 will promt you to set the mysql root password,
liblzo2-2 is required for python-tables.

# 2. cloning the application sources

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
application in /opt/spike, this will also be where the apache will be servering
the website from.

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

# 3. django/pinax configuration

### 3.1 database setup
*do this as root*

    mysql -p

in mysql console do

    CREATE DATABASE spike;
    USE spike;
    GRANT ALL PRIVILEGES ON spike.* TO spike@"%" IDENTIFIED BY "spike"

you can adjust the user and password ofc, we use spike:spike here

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

