##---IMPORTS

from django.contrib import admin
from .models import Algorithm, EvaluationBatch, Evaluation, EvaluationResults, EvaluationResultsImg

##---ADMINS

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

admin.site.register(EvaluationResults, EvaluationResultsAdmin)

class EvaluationResultsImgAdmin(admin.ModelAdmin):
    pass

admin.site.register(EvaluationResultsImg, EvaluationResultsImgAdmin)

##---MAIN

if __name__ == '__main__':
    pass
