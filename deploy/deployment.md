This file will detail the steps and issues concerning the deployment of the
spikesorting evaluation website application.

### CONTENTS ###

1. requirements
  1. platform and software
  2. webserver
2. settings and configs
  1. frontend settings
  2. backend settings
  3. celery task broker
3. other


# 1) requirements #

In this section the server requirements will be detailed.

## 1.1) PLATFORM AND SOFTWARE

We will assume a "Debian squeeze" as run on the g-node predata:

>   pmeier@predata:/opt/spike$ lsb_release  -a
>   No LSB modules are available.
> Distributor ID:	Debian
> Description:	Debian GNU/Linux 6.0.3 (squeeze)
> Release:	6.0.3
> Codename:	squeeze
> pmeier@predata:/opt/spike$ uname -a
>Linux predata 2.6.32-5-amd64 #1 SMP Thu Nov 3 03:41:26 UTC 2011 x86_64
GNU/Linux

Befor all we will need a suitable python environment. I suggest to use the
virtualenv package to set up the environment. A Python 2.7.x is suitable or
at least what the development was done with.

You will need "pip" to process the requirements.txt files.

The frontend uses django/pinax environment. The "requirements_pinax.txt" should
take care of all the necessary python packages for the frontend. In a later
iteration there will be unit tests to check the environment for compliance.

The backend uses a scipy/numpy/matplotlib environment as usual in scientific
computing in Python. The "requirements_spike_eval.txt" should take care of
all the neccessary python packages for the backend.

## 1.2 WEBSERVER ##

We will assume an "Apache2" webserver as run on the g-node predata.

The django/pinax frontend will be served by the apache2 using mod_wsgi. There
is a deploy.py in the project root that will produce a "wsgi.py" and an
"apache.conf" file in the project root.

## 1.3 FRONTEND SETTINGS ##

There are two files

## 1.4 BACKEND SETTINGS ##

## 1.5 CELERY TASK BROKER ##
