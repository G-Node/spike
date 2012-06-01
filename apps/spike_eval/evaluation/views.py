##---IMPORTS

from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import (
    Evaluation, EvaluationResults, EvaluationResultsImg)
from ..util import render_to

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
@render_to('spike_eval/evaluation/list.html')
def list(request, bid=None, tid=None, vid=None):
    """renders a list of available evaluations"""

    # inits and checks
    e_list = Evaluation.objects.filter(access=20)
    if request.user.is_authenticated():
        e_list = e_list | Evaluation.objects.filter(owner=request.user,
                                                    access=10)

    # filters
    if bid is not None:
        e_list = e_list.filter(trial__benchmark=bid)
    if tid is not None:
        e_list = e_list.filter(trial=tid)

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
@render_to('spike_eval/evaluation/detail.html')
def detail(request, eid):
    """renders details of an evaluation"""

    # init and checks
    e = get_object_or_404(Evaluation.objects.all(), id=eid)
    if not e.is_accessible(request.user):
        return HttpResponseForbidden(
            'You don\'t have rights to view this Evaluation.')
    er = e.evaluationresults_set.all()
    if er:
        er = sorted(er, cmp=sort_er, key=lambda x:x.gt_unit)
    image_results = e.evaluationresultsimg_set.all()

    # status check
    if e.task_state == 10:
        dt = datetime.now() - e.date_created
        if dt.days > 0:
            e.task_state = 0 # Failure
            e.task_log = '\n'.join([
                e.task_log or '',
                '',
                'Unrecoverable Processing-Error: idle time > 1day!'])
            e.save()

    # post request
    if request.method == 'POST':
        action = request.POST.get('action', None)
        if action == 'switch':
            if e.owner == request.user:
                e.switch()
        elif action == 'restart':
            s

    # response
    return {'e':e,
            'er':er,
            'image_results':image_results}

##---MAIN

if __name__ == '__main__':
    pass
