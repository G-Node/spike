from django.contrib import admin
from experiments.models import Experiment

class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('title', 'caption','date_created','owner','tags',)

admin.site.register(Experiment, ExperimentAdmin)
