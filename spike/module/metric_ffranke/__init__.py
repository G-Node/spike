##---IMPORTS

import os
from django.db import models

##---PACKAGE

__author__ = 'pmeier'
__version__ = '0.1'
__module__ = 'metric ffranke'
__module_path__ = os.path.split(os.path.split(__file__)[0])[1]
__has_summary__ = True

##---INIT

module = None
Module = None
try:
    Module = models.get_model('spike', 'module')
    module, created = Module.objects.get_or_create(
        name=__module__,
        version=__version__,
        path=__module_path__)
    if created is True:
        print 'just create module for:', __module__
        desc = 'no description'
        try:
            desc = open('readme.txt', 'r').read()
        except:
            pass
        finally:
            module.description = desc
            module.save()
except Exception, ex:
    print 'could not load module:', __module__
    print ex
finally:
    del os, models, Module, module

from .module import Module as module_cls
