# Celery setup instructions

## RabbitMQ Server

This is the AMQP implementation used to pass messages and store results.

### install (platform)

Assuming you are on a debian-esque linux, use the package manager to install:

    $ sudo aptitude install rabbitmq-server librabbitmq1

Else check http://www.rabbitmq.com/download.html for package for your platform.

### configuration (platform)

ref: https://docs.celeryproject.org/en/latest/getting-started/brokers/rabbitmq.html#broker-rabbitmq

install user, vhost and set permissions:

    $ rabbitmqctl add_user spike spike
    $ rabbitmqctl add_vhost spike_vhost
    $ rabbitmqctl set_permissions -p spike_vhost spike ".*" ".*" ".*"

you can now check the setting by using:

    $ rabbitmqctl status



## Celery python package

This is the python interface for the distributed task queue.

### install (python)

In your virtualenv, install:

    pip install celery==3.1.6

or use `deploy/requirements_celery.txt`.
