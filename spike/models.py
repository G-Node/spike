##---IMPORTS

from django.db.models import FileField
from django.core.files.storage import default_storage

##---RECEIVERS

def file_cleanup(sender, **kwargs):
    """http://djangosnippets.org/snippets/2744/

    File cleanup callback used to emulate the old delete
    behavior using signals. Initially django deleted linked
    files when an object containing a File/ImageField was deleted.

    Usage:

    >>> from django.db.models.signals import post_delete

    >>> post_delete.connect(file_cleanup, sender=MyModel, dispatch_uid="mymodel.file_cleanup")
    """

    for fieldname in sender._meta.get_all_field_names():
        try:
            field = sender._meta.get_field(fieldname)
        except:
            field = None
        if field and isinstance(field, FileField):
            inst = kwargs['instance']
            f = getattr(inst, fieldname)
            m = inst.__class__._default_manager
            if hasattr(f, 'path') and\
               default_storage.exists(f.path) and\
               not m.filter(**{'%s__exact' % fieldname: getattr(inst, fieldname)}).exclude(pk=inst._get_pk_val()):
                try:
                    #os.remove(f.path)
                    default_storage.delete(f.path)
                except:
                    pass

##---MAIN

if __name__ == '__main__':
    pass
