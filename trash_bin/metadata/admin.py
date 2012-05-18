from django.contrib import admin
from metadata.models import Section, Property

class SectionAdmin(admin.ModelAdmin):
    list_display = ('title','date_created',)

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title','date_created',)

admin.site.register(Section, SectionAdmin)
