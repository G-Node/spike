##---IMPORTS

from django.contrib import admin
from .models import Batch, Evaluation

##---ADMIN

class BatchAdmin(admin.ModelAdmin):
    pass

admin.site.register(Batch, BatchAdmin)

class EvaluationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Evaluation, EvaluationAdmin)

##---MAIN

if __name__ == '__main__':
    pass
