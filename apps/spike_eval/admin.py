##---IMPORTS

from django.contrib import admin
from .models import *

##---BENCHMARK

class BenchmarkAdmin(admin.ModelAdmin):
    pass

admin.site.register(Benchmark, BenchmarkAdmin)

class TrialAdmin(admin.ModelAdmin):
    pass

admin.site.register(Trial, TrialAdmin)

##---DATAFILE

class DatafileAdmin(admin.ModelAdmin):
    pass

admin.site.register(Datafile, DatafileAdmin)

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

##----METRIC

class MetricAdmin(admin.ModelAdmin):
    pass

admin.site.register(Metric, MetricAdmin)

##---RESULTS

class ResultAdmin(admin.ModelAdmin):
    pass

admin.site.register(Result, ResultAdmin)

class EvaluationResultsAdmin(admin.ModelAdmin):
    pass

admin.site.register(EvaluationResult, EvaluationResultsAdmin)

class EvaluationResultsImgAdmin(admin.ModelAdmin):
    pass

admin.site.register(EvaluationResultImg, EvaluationResultsImgAdmin)

##---MAIN

if __name__ == '__main__':
    pass
