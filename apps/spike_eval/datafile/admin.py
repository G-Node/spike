##---IMPORTS

from django.contrib import admin
from .models import Datafile

##---ADMINS

class DatafileAdmin(admin.ModelAdmin):
    pass

admin.site.register(Datafile, DatafileAdmin)

##---MAIN

if __name__ == '__main__':
    pass
