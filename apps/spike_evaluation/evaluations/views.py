##---IMPORTS

from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from spike_evaluation.evaluations.models import (
    Evaluation, EvaluationResults, EvaluationResultsImg)
from spike_evaluation.helpers import render_to

##---HELPERS

def sort_er(a, b):
    try:
        return cmp(int(a), int(b))
    except:
        try:
            int(a)
        except:
            return 1
        else:
            return -1

##---VIEWS

#@login_required
@render_to('spike_evaluation/evaluations/list.html')
def list(request, bid=None, rid=None, vid=None):
    """renders a list of available evaluations"""

    # inits and checks
    e_list = Evaluation.objects.filter(publication_state=1)
    if request.user.is_authenticated():
        e_list = e_list | Evaluation.objects.filter(owner=request.user,
                                                    publication_state=0)

    # filters
    if bid is not None:
        e_list = e_list.filter(
            original_file__datafile__record__benchmark=bid)
    if rid is not None:
        e_list = e_list.filter(original_file__datafile__record=rid)
    if vid is not None:
        e_list = e_list.filter(original_file=vid)

    # search terms
    search_terms = request.GET.get('search', '')
    if search_terms:
        e_list = (
            e_list.filter(algotithm__icontains=search_terms) |
            e_list.filter(description__icontains=search_terms) |
            e_list.filter(owner__icontains=search_terms))

    # response
    return {'e_list':e_list}

#@login_required
@render_to('spike_evaluation/evaluations/detail.html')
def detail(request, eid):
    """renders details of an evaluation"""

    # inits and checks
    e = get_object_or_404(Evaluation.objects.all(), id=eid)
    if not e.is_accessible(request.user):
        return HttpResponseForbidden(
            'You don\'t have rights to view this Evaluation.')
    er = e.evaluationresults_set.all()
    if er:
        er = sorted(er, cmp=sort_er, key=lambda x:x.gt_unit)
    image_results = e.evaluationresultsimg_set.all()

    # status check
    if e.processing_state == 10:
        dt = datetime.now() - e.date_created
        if dt.days > 0:
            e.processing_state = 0 # Failure
            e.evaluation_log = '\n'.join([
                e.evaluation_log or '',
                '',
                'Unrecoverable Processing-Error: idle time > 1day!'])
            e.save()

    # post request
    if request.method == 'POST':
        action = request.POST.get('action', None)
        if action == 'switch':
            if e.owner == request.user:
                e.switch()

    # response
    return {'e':e,
            'er':er,
            'image_results':image_results}

##---MAIN

if __name__ == '__main__':
    pass
