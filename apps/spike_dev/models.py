##---IMPORTS

from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel
from model_utils.managers import InheritanceManager

##---MODEL-REFS

Datafile = models.get_model('spike_eval', 'datafile')

##---MODELS

class Ref(models.Model):
    class Meta:
        app_label = 'spike_dev'

    name = models.TextField()


class Parent(TimeStampedModel):
    class Meta:
        app_label = 'spike_dev'

    objects = InheritanceManager()

    name = models.TextField()
    ref = models.ForeignKey('Ref')


class Child1(Parent):
    value = models.TextField()


class Child2(Parent):
    value = models.IntegerField()

##---MAIN

if __name__ == '__main__':
    pass
