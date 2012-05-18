from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'trash_folder.views.trashContents_Exps', name="deletedExperiments"),
    url(r'^deletedDatasets/$', 'trash_folder.views.trashContents_Datasets', name="deletedDatasets"),
    url(r'^deletedFiles/$', 'trash_folder.views.trashContents_Files', name="deletedFiles"),
)
