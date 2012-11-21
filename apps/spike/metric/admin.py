##---IMPORTS

from django.contrib import admin
from .models import Metric, Result

##---ADMINS

class MetricAdmin(admin.ModelAdmin):
    pass

admin.site.register(Metric, MetricAdmin)

class ResultAdmin(admin.ModelAdmin):
    pass

admin.site.register(Result, ResultAdmin)

##---MAIN

if __name__ == '__main__':
    pass
