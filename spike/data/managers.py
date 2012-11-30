##---IMPORTS

from django.db import models
from django.contrib.contenttypes.models import ContentType

__all__ = ['DataManager']

##---MANAGERS

class DataManager(models.Manager):
    """Data manager for any model"""

    def get_for(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id, object_id=obj.id)

##---MAIN

if __name__ == '__main__':
    pass
