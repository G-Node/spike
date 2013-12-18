##---IMPORTS

from django.contrib import admin
from .models import ResultDefaultVisual

##---ADMIN

class ResultDefaultVisualAdmin(admin.ModelAdmin):
    pass

admin.site.register(ResultDefaultVisual, ResultDefaultVisualAdmin)

##---MAIN

if __name__ == '__main__':
    pass
