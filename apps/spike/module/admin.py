##---IMPORTS

from django.contrib import admin
from .models import Module, Result

##---ADMINS

class ModuleAdmin(admin.ModelAdmin):
    pass

admin.site.register(Module, ModuleAdmin)

class ResultAdmin(admin.ModelAdmin):
    pass

admin.site.register(Result, ResultAdmin)

##---MAIN

if __name__ == '__main__':
    pass
