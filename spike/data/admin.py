##---IMPORTS

from django.contrib import admin
from .models import Data

##---ADMIN

class DataAdmin(admin.ModelAdmin):
    pass

admin.site.register(Data, DataAdmin)

##---MAIN

if __name__ == '__main__':
    pass
