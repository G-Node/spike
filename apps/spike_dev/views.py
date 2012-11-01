##---IMPORTS

from django.contrib import messages
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView
from spike_eval.forms import AlgorithmForm, SupplementaryForm
from spike_eval.util import render_to

##---MODEL-REFS

Algorithm = models.get_model('spike_eval', 'algorithm')

##---VIEWS

@render_to('../spike_eval/templates/spike_eval/spike_eval/algorithm/list.html')
def a_list(request):
    """renders a list of available algorithms"""

    # init and checks
    a_list = Algorithm.objects.all()
    a_form = None
    a_list_self = None
    if request.user.is_authenticated():
        a_list_self = Algorithm.objects.filter(added_by=request.user)

    # post request
    if request.method == 'POST':
        a_form = AlgorithmForm(request.POST)
        if a_form.is_valid():
            a = a_form.save(user=request.user)
            messages.success(request, 'Algorithm creation successful!')
            redirect(a)
        else:
            messages.error(request, 'Algorithm creation failed!')

    # search terms
    search_terms = request.GET.get('search', '')
    if search_terms:
        a_list = (
            a_list.filter(name__icontains=search_terms) |
            a_list.filter(added_by__username__icontains=search_terms))

    # response
    return {'a_list': a_list,
            'a_list_self': a_list_self,
            'a_form': a_form or AlgorithmForm(),
            'search_terms': search_terms}


class AlgorithmListView(ListView):
    context_object_name = 'a_list'
    template_name = '../spike_eval/templates/spike_eval/spike_eval/algorithm/list.html'
    queryset = Algorithm.objects.all()

    ## methods

    def get_context_data(self, **kwargs):
        context = super(AlgorithmListView, self).get_context_data(**kwargs)
        a_form = None
        a_list_self = None

        if self.request.user.is_authenticated():
            a_list_self = self.queryset.filter(added_by=self.request.user)

        # post request
        if self.request.method == 'POST':
            a_form = AlgorithmForm(self.request.POST)
            if a_form.is_valid():
                a = a_form.save(user=self.request.user)
                messages.success(self.request, 'Algorithm creation successful!')
                redirect(a)
            else:
                messages.error(self.request, 'Algorithm creation failed!')

        # search terms
        search_terms = self.request.GET.get('search', '')
        if search_terms:
            a_list = (
                self.queryset.filter(name__icontains=search_terms) |
                self.queryset.filter(added_by__username__icontains=search_terms))

        # response
        print context
        context['a_list_self'] = a_list_self
        context['a_form'] = a_form or AlgorithmForm()
        context['search_terms'] = search_terms
        print context
        return context


class CreateTest(CreateView):
    pass


def display_meta(request):
    values = request.META.items()
    values.sort()
    html = []
    for k, v in values:
        html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, v))
    return HttpResponse('<table>%s</table>' % '\n'.join(html))


@render_to('spike_dev/something.html')
def something(request):
    # init
    ctx_list = []

    # build something
    ctx_list.append(Context('PETER', '_unit0'))

    # return
    return {'ctx_list': ctx_list}

##---CLASS

class Context(object):
    def __init__(self, name, temp):
        self.name = name
        self.temp = 'spike_dev/%s.html' % temp

##---MAIN

if __name__ == '__main__':
    pass
