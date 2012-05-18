from django.contrib import admin
from spike_evaluation.dfiles.models import Datafile

class DatafileAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_created','added_by', 'filetype')

admin.site.register(Datafile, DatafileAdmin)
