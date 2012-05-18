"""
The Docs site will have hirarchy like:

Topic
 |-- Article
 |     |-- Section
 |     |-- Section
 |     *
 |-- Article
 *     |-- Section
       |-- Section
       *
"""

##---IMPORTS

from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

##---MODELS

class Topic(models.Model):
    """Topic model"""

    ## fields

    title = models.CharField(max_length=255)
    sort = models.IntegerField(default=0)
    published = models.BooleanField(default=False)

    ## set mappings

    def articles(self):
        return self.article_set.order_by('sort')

    ## interface

    def switch(self):
        self.published = not self.published
        self.save()

    ## special methods

    def __unicode__(self):
        return self.title


class Article(models.Model):
    """Article model"""

    ## fields

    title = models.CharField(max_length=255)
    sort = models.IntegerField(default=0)
    published = models.BooleanField(default=False)

    topic = models.ForeignKey(Topic)

    @models.permalink
    def get_absolute_url(self):
        return reverse('evaldocs-article', kwargs={'id':self.pk})

    ## set mappings

    def sections(self):
        return self.section_set.order_by('sort')

    ## interface

    def switch(self):
        self.published = not self.published
        self.save()

    ## special methods

    def __unicode__(self):
        return self.title


class Section(models.Model):
    """Section model"""

    ## fields

    title = models.CharField(max_length=255)
    sort = models.IntegerField(default=0)
    published = models.BooleanField(default=False)

    content = models.TextField(blank=True, null=True)

    article = models.ForeignKey(Article)

    @models.permalink
    def get_absolute_url(self):
        return reverse('evaldocs-section', kwargs={'id':self.pk})

    ## interface

    def switch(self):
        self.published = not self.published
        self.save()

    ## special methods

    def __unicode__(self):
        return self.title
