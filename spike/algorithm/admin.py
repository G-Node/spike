##---IMPORTS

from django.contrib import admin
from .models import Algorithm

##---ADMIN

class AlgorithmAdmin(admin.ModelAdmin):
    pass

admin.site.register(Algorithm, AlgorithmAdmin)

##---MAIN

if __name__ == '__main__':
    pass
