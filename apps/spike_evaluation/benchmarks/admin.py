from django.contrib import admin
from spike_evaluation.benchmarks.models import Benchmark

class BenchmarkAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'date_created', 'added_by')

admin.site.register(Benchmark, BenchmarkAdmin)
