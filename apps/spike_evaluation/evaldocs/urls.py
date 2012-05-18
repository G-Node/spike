from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spike_evaluation.evaldocs.views',
    url(r'^$', 'topic_view', name='evaldocs'),
    url(r'^article/(?P<idx>\d+)/$', 'article_view', name='evaldocs-article'),
    url(r'^section/(?P<idx>\d+)$', 'section_view', name='evaldocs-section'),
    )
