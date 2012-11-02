##---IMPORTS

from django.contrib import admin
from .models import Algorithm, Batch, Benchmark, Evaluation, Trial

##---BENCHMARK

class BenchmarkAdmin(admin.ModelAdmin):
    pass

admin.site.register(Benchmark, BenchmarkAdmin)

class TrialAdmin(admin.ModelAdmin):
    pass

admin.site.register(Trial, TrialAdmin)

##---ALGORITHM

class AlgorithmAdmin(admin.ModelAdmin):
    pass

admin.site.register(Algorithm, AlgorithmAdmin)

##---EVALUATION

class BatchAdmin(admin.ModelAdmin):
    pass

admin.site.register(Batch, BatchAdmin)

class EvaluationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Evaluation, EvaluationAdmin)

##---MAIN

if __name__ == '__main__':
    pass
