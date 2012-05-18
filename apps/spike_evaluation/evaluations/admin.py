from django.contrib import admin
from spike_evaluation.evaluations.models import Evaluation

class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('algorithm', 'description', 'owner', 'processing_state', 'added_by')

admin.site.register(Evaluation, EvaluationAdmin)
