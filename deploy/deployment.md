This file will detail the steps and issues concerning the deployment of the
spikesorting evaluation website application.

### CONTENTS

1. platform requirements
    1. platform and software
    2. python
    3. webserver
    4. database
2. settings and configs
    1. frontend settings
    2. backend settings
    3. celery task broker
3. other


# 1) PLATTFORM REQUIREMENTS

In this section the server requirements will be detailed.

## 1.1) PLATFORM AND SOFTWARE

We will assume a "Debian squeeze" as run on the g-node predata:

    pmeier@predata:/opt/spike$ lsb_release  -a
    No LSB modules are available.
    Distributor ID:	Debian
    Description:	Debian GNU/Linux 6.0.3 (squeeze)
    Release:	6.0.3
    Codename:	squeeze
    pmeier@predata:/opt/spike$ uname -a
    Linux predata 2.6.32-5-amd64 #1 SMP Thu Nov 3 03:41:26 UTC 2011 x86_64 GNU/Linux

## 1.2 PYTHON

Befor all we will need a suitable python environment. I suggest to use the
virtualenv package to set up the environment. A Python 2.7.x is suitable or
at least what the development was done with.

I recommend to use "pip" to process the requirements.txt files. Else the
python packages have to be installed manually.

The frontend uses django/pinax environment. The "requirements_pinax.txt" should
take care of all the necessary python packages for the frontend. In a later
iteration there will be unit tests to check the environment for compliance.

The backend uses a scipy/numpy/matplotlib environment as usual in scientific
computing in Python. The "requirements_spike_eval.txt" should take care of
all the neccessary python packages for the backend.

## 1.3 WEBSERVER

We will assume an "Apache2" webserver as run on the g-node predata.

The django/pinax frontend will be served by the apache2 using mod_wsgi. There
is a deploy.py in the project root that will produce a "wsgi.py" and an
"apache.conf" file in the project root, fit to use that wsgi.py. The "apache
.conf" and apache logs will be stored in ./apache.

## 1.4 DATABASE

A databse will be used, for the frontend mostly. The standard database yould
be a MySQL database, optionally postgresql (not required though). We will
need schema with full edit permissions set to the database user.

# SETTINGS AND CONFIGS

## 2.1 FRONTEND SETTINGS

Copy the "settings_local.temp.py" in the project root and name it
"settings_local.py". Try to configure everthing relevant as needed. I will
go over the sections here:

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

### 2.1.1 FRONTEND CRONTAB

The frontend uses django-mailer with the database as backend for email
queueing. So to actually send the emails

    python manage.py send_mail

has to be called periodically using a crontab. The crontab for this would
look like this:

    * * * * * cd /path/to/spike; python manage.py send_mail >> /path/to/spike/log/cron_mail.log 2>&1
    00,20,40 * * * * cd /path/to/spike; python manage.py retry_deferred >> /path/to/spike/log/cron_mail_deferred.log 2>&1

## 2.2 BACKEND SETTINGS

None so far. I guess ther will be a .matplotlib.cfg file soon when I iterate
the figures.

## 2.3 CELERY TASK BROKER

Since the evaluations can be quite compute-intensive Andrey decided to use a
distrubuted task queue for these things. All baackend tasks that are triggered
from the frontend are implemented as celery tasks and are executed in the
distributed environment. If the celery is available (determined by import of
djcelery without an ImportException), the celery backend will be used as
default.

To install celery please refer use the requirements_celery.txt or install
the django-celery python package and its requirements.

If the celery task broker is running on a non-standard uri, please adjust the
BROKER_URL in settings_celery.py. The results backend is set to 'database'
and defaults to the same databse the frontend is using.

The task broker has to be started as a process running along with the
application at all times. I suggest taking care of this with a checking
crontab or something else.

The task broker is started using the command

    python manage.py celeryd -l info

## 3. STEP BY STEP INSTALATION

