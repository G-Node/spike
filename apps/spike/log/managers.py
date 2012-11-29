##---IMPORTS

from django.db import models
from django.contrib.contenttypes.models import ContentType

__all__ = ['LogManager']

##---MANAGERS

class LogManager(models.Manager):
    """LogItem manager"""

    def get_for(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id, object_id=obj.id).order_by('modified')

##---MAIN

if __name__ == '__main__':
    pass
