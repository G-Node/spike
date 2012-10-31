##---IMPORTS

from django.contrib import messages
from django.db import models
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from ..forms import AlgorithmForm, SupplementaryForm
from ..util import render_to

##---MODEL-REFS

Algorithm = models.get_model('spike_eval', 'algorithm')

##---VIEWS

@render_to('spike_eval/algorithm/detail.html')
def a_detail(request, aid):
    """renders details of an algorithm"""

    # init and checks
    a = get_object_or_404(Algorithm.objects.all(), id=aid)
    a_form = None
    s_form = None

    # post request
    if request.method == 'POST':
        print request.POST
        if 'a_edit' in request.POST:
            a_form = AlgorithmForm(request.POST, instance=a)
            if a_form.is_valid():
                a = a_form.save()
                messages.success(request, 'Algorithm edit successful!')
            else:
                messages.warning(request, 'Algorithm edit failed!')
        elif 's_create' in request.POST:
            s_form = SupplementaryForm(request.POST, request.FILES)
            if s_form.is_valid():
                s = s_form.save(user=request.user, obj=a)
                messages.success(
                    request,
                    'Supplementary creation successful: \'%s\'' % s)
            else:
                messages.warning(request, 'Supplementary creation failed!')
        elif 's_delete' in request.POST:
            try:
                DFM = models.get_model('datafile', 'datafile')
                sid = int(request.POST['s_id'])
                s = get_object_or_404(DFM.objects, id=sid)
                s.delete()
                messages.success(request, 'Supplementary deleted!')
            except:
                messages.error(request, 'Supplementary delete failed!')

    # response
    return {'a': a,
            'a_form': a_form or AlgorithmForm(instance=a),
            's_form': s_form or SupplementaryForm()}


@render_to('spike_eval/algorithm/list.html')
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

##---MAIN

if __name__ == '__main__':
    pass
