##---IMPORTS

from django.contrib import admin
from .models.algorithm import Algorithm
from .models.benchmark import Benchmark, Trial
from .models.datafile import Datafile
from .models.evaluation import EvaluationBatch, Evaluation, EvaluationResult, EvaluationResultImg

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

##---EVALUATION

class AlgorithmAdmin(admin.ModelAdmin):
    pass

admin.site.register(Algorithm, AlgorithmAdmin)

class EvaluationBatchAdmin(admin.ModelAdmin):
    pass

admin.site.register(EvaluationBatch, EvaluationBatchAdmin)

class EvaluationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Evaluation, EvaluationAdmin)

class EvaluationResultsAdmin(admin.ModelAdmin):
    pass

admin.site.register(EvaluationResult, EvaluationResultsAdmin)

class EvaluationResultsImgAdmin(admin.ModelAdmin):
    pass

admin.site.register(EvaluationResultImg, EvaluationResultsImgAdmin)

##---MAIN

if __name__ == '__main__':
    pass
