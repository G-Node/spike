from django.contrib import admin
from timeseries.models import TimeSeries

class TimeSeriesAdmin(admin.ModelAdmin):
    list_display = ('title','date_created',)

admin.site.register(TimeSeries, TimeSeriesAdmin)
