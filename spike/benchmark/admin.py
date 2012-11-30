##---IMPORTS

from django.contrib import admin
from .models import Benchmark, Trial

##---ADMIN

class BenchmarkAdmin(admin.ModelAdmin):
    pass

admin.site.register(Benchmark, BenchmarkAdmin)

class TrialAdmin(admin.ModelAdmin):
    pass

admin.site.register(Trial, TrialAdmin)

##---MAIN

if __name__ == '__main__':
    pass
