from django.contrib import admin
from datasets.models import RDataset

class RDatasetAdmin(admin.ModelAdmin):
    list_display = ('title', 'caption','date_added','owner','tags',)

admin.site.register(RDataset, RDatasetAdmin)
