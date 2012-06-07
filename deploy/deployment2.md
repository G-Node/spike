

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




