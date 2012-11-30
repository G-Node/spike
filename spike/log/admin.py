##---IMPORTS

from django.contrib import admin
from .models import Log

##---ADMIN

class LogAdmin(admin.ModelAdmin):
    pass

admin.site.register(Log, LogAdmin)

##---MAIN

if __name__ == '__main__':
    pass
