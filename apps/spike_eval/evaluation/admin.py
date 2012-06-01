##---IMPORTS

from django.contrib import admin
from .models import Algorithm, Evaluation

##---ADMINS

class AlgorithmAdmin(admin.ModelAdmin):
    pass

admin.site.register(Algorithm, AlgorithmAdmin)

class EvaluationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Evaluation, EvaluationAdmin)

##---MAIN

if __name__ == '__main__':
    pass
