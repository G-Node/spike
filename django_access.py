import os
import sys

# just import this module and you may play with G-Node Django classes
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
#SYSTEM_ROOT = os.path.normpath(os.path.join(os.getcwd(), ".."))
PROJECT_NAME = PROJECT_PATH[PROJECT_PATH.rfind('/') + 1:] # just in case

# some path settings - order matters


to_pythonpath = (
    './',
    PROJECT_PATH,
    os.path.join(PROJECT_PATH, 'apps/'),
    os.path.join(PROJECT_PATH, 'apps/ext/'),
    os.path.join(PROJECT_PATH, 'apps/spike_evaluation/'),
    os.path.join(PROJECT_PATH, 'apps/ext/pinax/'),
    os.path.join(PROJECT_PATH, 'apps/ext/pinax/apps/'),
    )

for path in to_pythonpath:
    #path = os.path.abspath(os.path.join(SYSTEM_ROOT, p))
    if path not in sys.path:
        sys.path.append(path)

#os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % PROJECT_NAME
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

"""
Examples

1. Password reset
import django_access
from django.contrib.auth.models import User
menz = User.objects.get(username="andrey")
menz.set_password("pass")
menz.save()


2. Http Request56
import django_access
from django.http import HttpRequest
from django.contrib.auth.models import User
from neo_api.views import create

r = HttpRequest()
menz = User.objects.get(username="andrey")
r.user = menz
r.method = "POST"
r._read_started = False

# eh.. does not work


"""
