__author__ = 'pmeier'
__version__ = '0.1'
__module__ = 'default visual'
__module_path__ = 'default_visual'

mod = None
try:
    import os
    from django.db import models

    Module = models.get_model('spike', 'module')
    try:
        mod, created = Module.objects.get_or_create(
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
                mod.description = desc
                mod.save()
    except:
        print 'error loading module model!!'
except ImportError:
    pass
finally:
    del os
    del models
    del Module
    del mod
