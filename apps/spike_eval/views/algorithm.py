##---IMPORTS

from django.contrib import messages
from django.db import models
from django.shortcuts import get_object_or_404, redirect
from ..forms import AlgorithmForm, SupplementaryForm
from ..util import render_to

##---MODEL-REFS

Algorithm = models.get_model('spike_eval', 'algorithm')

##---VIEWS

@render_to('spike_eval/algorithm/list.html')
def list(request):
    """renders a list of available algorithms"""

    # init and checks
    al_list = Algorithm.objects.all()
    al_form = None

    # post request
    if request.method == 'POST':
        al_form = AlgorithmForm(request.POST)
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
            'al_form': al_form or AlgorithmForm(),
            'search_terms': search_terms}


@render_to('spike_eval/algorithm/detail.html')
def detail(request, alid):
    """renders algorithm detail"""

    # init and checks
    try:
        al = Algorithm.objects.get(pk=alid)
    except Exception, ex:
        messages.error(request, 'You are not allowed to view or modify this Algorithm: %s' % ex)
        return redirect('al_list')
    al_form = None
    sf_form = None

    # post request
    if request.method == 'POST':
        if 'al_edit' in request.POST:
            al_form = AlgorithmForm(request.POST, instance=al)
            if al_form.is_valid():
                al = al_form.save()
                messages.success(request, 'Algorithm edit successful')
            else:
                messages.error(request, 'Algorithm edit failed')
        elif 'sf_create' in request.POST:
            sf_form = SupplementaryForm(request.POST, request.FILES)
            if sf_form.is_valid():
                sf = sf_form.save(user=request.user, obj=al)
                messages.success(
                    request,
                    'Supplementary creation successful: "%s"' % sf)
            else:
                messages.error(request, 'Supplementary creation failed')
        elif 'sf_delete' in request.POST:
            try:
                sfid = int(request.POST['sf_id'])
                al.datafile_set.get(pk=sfid).delete()
                messages.success(request, 'Supplementary deleted!')
            except:
                messages.error(request, 'Supplementary delete failed')

    # response
    return {'al': al,
            'sf_list': al.datafile_set.all(),
            'al_form': al_form or AlgorithmForm(instance=al),
            'sf_form': sf_form or SupplementaryForm()}

##---MAIN

if __name__ == '__main__':
    pass
