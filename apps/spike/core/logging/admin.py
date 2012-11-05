##---IMPORTS

from django.contrib import admin
from .models import LogItem

##---ADMIN

class LogItemAdmin(admin.ModelAdmin):
    pass

admin.site.register(LogItem, LogItemAdmin)

##---MAIN

if __name__ == '__main__':
    pass
