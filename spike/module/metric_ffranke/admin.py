##---IMPORTS

from django.contrib import admin
from .models import ResultMetricFFranke

##---ADMIN

class ResultMetricFFrankeAdmin(admin.ModelAdmin):
    pass

admin.site.register(ResultMetricFFranke, ResultMetricFFrankeAdmin)

##---MAIN

if __name__ == '__main__':
    pass
