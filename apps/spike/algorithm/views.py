##---IMPORTS

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import redirect
from ..forms import AlgorithmForm, AppendixForm
from ..util import render_to

##---MODEL-REFS

Algorithm = models.get_model('spike', 'algorithm')

##---VIEWS

@render_to('spike/algorithm/list.html')
def list(request):
    """renders a list of available algorithms"""

    # init and checks
    al_list = Algorithm.objects.all()
    al_form = None

    # post request
    if request.method == 'POST':
        al_form = AlgorithmForm(data=request.POST)
        if al_form.is_valid():
            al = al_form.save(user=request.user)
            messages.success(request, 'Algorithm creation successful')
            return redirect(al)
        else:
            messages.error(request, 'Algorithm creation failed')

    # search terms
    search_terms = request.GET.get('search', '')
    if search_terms:
        al_list = (al_list.filter(name__icontains=search_terms) |
                   al_list.filter(owner__username__icontains=search_terms))

    # response
    return {'al_list': al_list,
            'al_form': al_form or AlgorithmForm(initial={'owner': request.user}),
            'search_terms': search_terms}


@render_to('spike/algorithm/detail.html')
def detail(request, pk):
    """renders details for a particular algorithm"""

    # init and checks
    try:
        al = Algorithm.objects.get(pk=pk)
    except Exception, ex:
        messages.error(request, 'You are not allowed to view or modify this Algorithm: %s' % ex)
        return redirect('al_list')
    al_form = None
    ap_form = None

    # post request
    if request.method == 'POST':
        if 'al_edit' in request.POST:
            al_form = AlgorithmForm(data=request.POST, instance=al)
            if al_form.is_valid():
                al = al_form.save()
                messages.success(request, 'Algorithm edit successful')
            else:
                messages.error(request, 'Algorithm edit failed')
        elif 'ap_create' in request.POST:
            ap_form = AppendixForm(data=request.POST, files=request.FILES, obj=al)
            if ap_form.is_valid():
                ap = ap_form.save()
                messages.success(request, 'Appendix creation successful: "%s"' % ap)
            else:
                messages.error(request, 'Appendix creation failed')

    # response
    return {'al': al,
            'appendix': al.datafile_set.filter(kind='appendix'),
            'al_form': al_form or AlgorithmForm(instance=al),
            'ap_form': ap_form or AppendixForm(obj=al)}


@login_required
def delete(request, pk):
    """delete algorithm"""

    try:
        al = Algorithm.objects.get(pk=pk)
        assert al.is_editable(request.user), 'insufficient permissions'
        Algorithm.objects.get(pk=pk).delete()
        messages.success(request, 'Algorithm "%s" deleted' % al)
    except Exception, ex:
        messages.error(request, 'Algorithm not deleted: %s' % ex)
    finally:
        return redirect('al_list')

##---MAIN

if __name__ == '__main__':
    pass
