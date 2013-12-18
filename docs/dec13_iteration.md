# SPIKESORTING EVALUATION WEBSITE (SEW)

# *DECEMBER 2013 ITERATION*

## 1. Mission Statement

The project has been stagnant in its current form for about 12 month. The prototype implementation (SEW1) based on the pinax framework, hosted at the German Neuroinformatics Node (spike.g-node.org), has proven fragile. Issues are 1) the unstable distributed task queue backend, 2) unreliable email sending interrupting the account creation and activation workflow, 3) unfinished codebase for the new modular components and 4) no project management and low personnel assets.

After this iteration a new codebase and database should be available to resume operations, leading to SEW2. Dependancy on pinax is to be relaxed. Deadline to resume operations is 31. December, 2013.

**Primary goals:**

* solid signup and user account interaction
* merging the codebase into a master branch, and setting up a new instance [NI]
* slacking down the complexity of using the distributed task queue

**Secondary goals:**

* reach a stable frontend<->backend interoperability
* version upgrades for django stack (django 1.6)
* remove pinax references
* monitoring and report scheduling (watchdog app, nagios)

## 2. Situation Report

### 2.1 `celery` version upgrade

Celery has upgraded by a minor version to 3.1 branch. Current version is 3.1.6. `django-celery` is obsolete. Django is now supported directly from the celery codebase. This will trim down the effort for setting up and operating the application.

SEW2:

* upgrade to celery 3.1.6
* broker RabbitMQ

### 2.2 Pinax

Some pinax components prove to be problematic. Esp. `django-mailer` has lead to issues with signup and conversion. We reached where added functionality in the core django does not justify using the pinax packages anymore.

SEW2:

* remove django-mailer
* remove django-user-accounts

### 2.3 Monitoring

Lacking an operator continuously watching the environment and application, we (developers and staff) have to be the first to know when something is out of bounds, not hte users!

A watchdog application that controlling all parts of the stack on a daily basis should address this sufficiently. With email reports in case of default.

## 3. Actions

### 3.1 Pinax component replacements

### 3.2 Monitoring and control

Installed `monit`, monitoring dashboard is reachable under http://spike.g-node.org:2812 . Need to be fleshed with monitors for:
* apache
* rabbitmq
* celery workers
* sshd

### 3.3 Celery version upgrade and changes

## 4. SEW2 anatomy

## X. References

`celery`: www.celeryproject.org
`pinax`: www.pinaxproject.com
