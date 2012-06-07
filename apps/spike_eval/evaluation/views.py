##---IMPORTS

from datetime import datetime
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .models import Algorithm, Evaluation
from ..forms import AlgorithmForm, SupplementaryForm
from ..tasks import start_eval
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

@render_to('spike_eval/evaluation/list.html')
def list(request, bid=None, tid=None):
    """renders a list of available evaluations"""

    # init and checks
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
        if 'switch' in request.POST:
            if e.owner == request.user:
                e.switch()
        elif 'restart' in request.POST:
            # TODO: tidy up the old results
            rval = start_eval(e.id)
            messages.info(request, 'Evalulation is been restarted!')

    # response
    return {'e':e,
            'er':er,
            'image_results':image_results}


@render_to('spike_eval/evaluation/algo.html')
def algo(request, aid):
    """renders details of an algorithm"""

    # init and checks
    a = get_object_or_404(Algorithm.objects.all(), id=aid)
    a_form = None
    s_form = None

    # post request
    if request.method == 'POST':
        if '' in request.POST:
            a_form = AlgorithmForm(request.POST, instance=a)
            if a_form.is_valid():
                a = a_form.save()
                messages.success(request, 'Algorithm edit successful!')
            else:
                messages.warning(request, 'Algorithm edit failed!')
        elif '' in request.POST:
            s_form = SupplementaryForm(request.POST, request.FILES)
            if s_form.is_valid():
                s = s_form.save(user=request.user, obj=b)
                messages.success(
                    request,
                    'Supplementary creation successful: \'%s\'' % s)
            else:
                messages.warning(request, 'Supplementary creation failed!')

    if not a_form:
        a_form = AlgorithmForm(instance=a)
    if not s_form:
        s_form = SupplementaryForm()

    # response
    return {'a':a,
            'a_form':a_form,
            's_form':s_form}

##---MAIN

if __name__ == '__main__':
    pass
