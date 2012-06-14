##---IMPORTS

from datetime import datetime
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .models import Algorithm, Evaluation, EvaluationBatch
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
def list(request, bid=None):
    """renders a list of available evaluations"""

    # evaluation batch list
    e_list = EvaluationBatch.objects.filter(access=20)
    e_list_self = None
    if request.user.is_authenticated():
        if not request.user.is_superuser:
            e_list |= EvaluationBatch.objects.filter(
                added_by=request.user, access=10)
        else:
            e_list = EvaluationBatch.objects.all()
        e_list_self = EvaluationBatch.objects.filter(added_by=request.user)

    # filters
    if bid is not None:
        e_list = e_list.filter(benchmark=bid)
        e_list_self = e_list_self.filter(benchmark=bid)

    # search terms
    search_terms = request.GET.get('search', '')
    if search_terms:
        e_list = (
            e_list.filter(algorithm__icontains=search_terms) |
            e_list.filter(description__icontains=search_terms) |
            e_list.filter(added_by__icontains=search_terms) |
            e_list.filter(benchmark__icontains=search_terms))

    # response
    return {'e_list':e_list,
            'e_list_self':e_list_self,
            'search_terms':search_terms}


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



    # response
    return {'e':e,
            'er':er,
            'image_results':image_results}


@render_to('spike_eval/evaluation/batch.html')
def batch(request, ebid):
    """renders an evaluation batch"""

    # init and checks
    eb = get_object_or_404(EvaluationBatch.objects.all(), id=ebid)
    if not eb.is_accessible(request.user):
        return HttpResponseForbidden(
            'You don\'t have rights to view this Evaluation.')

    # post request
    if request.method == 'POST':
        if 'switch' in request.POST:
            if eb.added_by == request.user:
                eb.switch()
                messages.success(request, 'switch successful!')
        elif 'restart' in request.POST:
            # TODO: tidy up the old results
            print request.GET
            print request.POST
            eid = request.POST.get('restart_eid', None)
            if eid:
                start_eval(eid)
                messages.info(request, 'Evalulation is been restarted!')
            else:
                messages.error(request, 'Evalulation restart failed!')

    # response
    return {'eb':eb}


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
