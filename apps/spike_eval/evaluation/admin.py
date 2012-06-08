##---IMPORTS

from django.contrib import admin
from .models import Algorithm, Evaluation, EvaluationBatch

##---ADMINS

class AlgorithmAdmin(admin.ModelAdmin):
    pass

admin.site.register(Algorithm, AlgorithmAdmin)

class EvaluationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Evaluation, EvaluationAdmin)

class EvaluationBatchAdmin(admin.ModelAdmin):
    pass

admin.site.register(EvaluationBatch, EvaluationBatchAdmin)

##---MAIN

if __name__ == '__main__':
    pass
