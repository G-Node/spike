## evaldocs views


##---IMPORTS

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from evaldocs.models import Topic, Article, Section
from evaldocs.forms import TopicForm, ArticleForm, SectionForm
from helpers import render_to

##---CONSTANTS

TABLE = {
    'topic':Topic,
    'article':Article,
    'section':Section}
FORM = {
    'topic':TopicForm,
    'article':ArticleForm,
    'section':SectionForm}

##---VIEWS

@render_to('spike_evaluation/evaldocs/toc.html')
def topic_view(request):
    """render the table of contents"""

    # post request
    if request.method == 'POST' and request.user:
        try:
            assert request.user.is_authenticated()
            assert request.user.groups.filter(name='evaldocu')
            action = request.POST.get('action', None)
            assert action in ['create', 'switch', 'edit', 'delete']
            type = request.POST.get('type', None)
            assert type in ['topic', 'article', 'section']
            id = request.POST.get('id', None)
            form = FORM[type](request.POST)
            table = TABLE[type]
            if action == 'create':
                if form.is_valid():
                    obj = form.save(commit=False)
                    if type == 'article':
                        fk = get_object_or_404(Topic.objects.all(), id=id)
                        obj.topic = fk
                    if type == 'section':
                        fk = get_object_or_404(Article.objects.all(), id=id)
                        obj.article = fk
                    obj.save()
                    messages.info(
                        request,
                        'Successfully created %s \'%s\'' % (type, obj.title))
                else:
                    messages.warning(request, '%s creation failed!' % type)
            if action == 'switch':
                obj = get_object_or_404(table.objects.all(), id=id)
                obj.published = not obj.published
                obj.save()
                messages.info(request, 'Switched \'%s\'' % obj.title)
            elif action == 'edit':
                if form.is_valid():
                    obj = get_object_or_404(table.objects.all(), id=id)
                    obj.title = form.cleaned_data['title']
                    obj.sort = form.cleaned_data['sort']
                    if 'content' in form.cleaned_data:
                        obj.content = form.cleaned_data['content']
                    obj.save()
                    messages.warning(
                        request, 'Successfully edited %s \'%s\'' % (type, obj))
                else:
                    messages.warning(
                        request, '%s creation failed %s' % type)
            elif action == 'delete':
                obj = get_object_or_404(table.objects.all(), id=id)
                obj.delete()
                messages.info('Deleted %s \'%s\'' % (type, obj.title))
        except:
            messages.error(request, 'Sorry, that did not work out :/')

    # build forms and data
    f_edit_t = None
    f_edit_a = None
    f_edit_s = None
    topics = Topic.objects.order_by('sort')
    if not request.user.groups.filter(name='evaldocu'):
        topics = topics.filter(published=True)
    else:
        f_edit_t = TopicForm()
        f_edit_a = ArticleForm()
        f_edit_s = SectionForm()
    return {'topics':topics,
            'f_edit_t':f_edit_t,
            'f_edit_a':f_edit_a,
            'f_edit_s':f_edit_s}


@render_to('spike_evaluation/evaldocs/article.html')
def article_view(request, idx):
    if request.method == 'POST' and request.user:
        try:
            assert request.user.is_authenticated()
            assert request.user.groups.filter(name='evaldocu')
            action = request.POST.get('action', None)
            assert action in ['create', 'switch', 'edit', 'delete']
            type = request.POST.get('type', None)
            assert type in ['topic', 'article', 'section']
            id = request.POST.get('id', None)
            form = FORM[type](request.POST)
            table = TABLE[type]
            if action == 'create':
                if form.is_valid():
                    obj = form.save(commit=False)
                    if type == 'article':
                        fk = get_object_or_404(Topic.objects.all(), id=id)
                        obj.topic = fk
                    if type == 'section':
                        fk = get_object_or_404(Article.objects.all(), id=id)
                        obj.article = fk
                    obj.save()
                    messages.info(
                        request,
                        'Successfully created %s \'%s\'' % (type, obj.title))
                else:
                    messages.warning(request, '%s creation failed!' % type)
            if action == 'switch':
                obj = get_object_or_404(table.objects.all(), id=id)
                obj.published = not obj.published
                obj.save()
                messages.info(request, 'Switched \'%s\'' % obj.title)
            elif action == 'edit':
                if form.is_valid():
                    obj = get_object_or_404(table.objects.all(), id=id)
                    obj.title = form.cleaned_data['title']
                    obj.sort = form.cleaned_data['sort']
                    if 'content' in form.cleaned_data:
                        obj.content = form.cleaned_data['content']
                    obj.save()
                    messages.info(
                        request,
                        'Successfully edited %s \'%s\'' % (type, obj.title))
                else:
                    messages.warning(request, '%s creation failed!' % type)
            elif action == 'delete':
                obj = get_object_or_404(table.objects.all(), id=id)
                obj.delete()
                messages.info(request, 'Deleted %s \'%s\'' % (type, obj))
        except:
            messages.error(request, 'Sorry, that did not work out :/')

    # build forms and data
    f_edit_t = None
    f_edit_a = None
    f_edit_s = None
    article = get_object_or_404(Article, id=idx)
    topic = article.topic
    sections = article.section_set.all()
    if not request.user.groups.filter(name='evaldocu'):
        sections = sections.filter(published=True)
    else:
        f_edit_t = TopicForm()
        f_edit_a = ArticleForm()
        f_edit_s = SectionForm()
    return {'topic':topic,
            'article':article,
            'sections':sections,
            'f_edit_t':f_edit_t,
            'f_edit_a':f_edit_a,
            'f_edit_s':f_edit_s}


def section_view(request, idx):
    sec = get_object_or_404(Section, id=idx)
    target = reverse('evaldocs-article', args=(sec.article.id,))
    target += '#sec-%s' % sec.id
    return redirect(target)

##---MAIN

if __name__ == '__main__':
    pass
