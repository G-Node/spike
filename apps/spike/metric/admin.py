##---IMPORTS

from django.contrib import admin
from .models import Metric, Result, EvaluationResult, EvaluationResultImg

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
