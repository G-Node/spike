##---IMPORTS

import zipfile
from StringIO import StringIO
from django.contrib import messages
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.defaultfilters import slugify
from .models import Algorithm, Evaluation, EvaluationBatch
from ..forms import AlgorithmForm, SupplementaryForm, EvalBatchEditForm
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
def elist(request, bid=None):
    """renders a list of available evaluations"""

    # evaluation batch list
    e_list = EvaluationBatch.objects.filter(access=20)
    e_list_self = None
    if request.user.is_authenticated():
        if request.user.is_superuser:
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
    return {'e_list': e_list,
            'e_list_self': e_list_self,
            'search_terms': search_terms}


@render_to('spike_eval/evaluation/batch.html')
def batch(request, ebid):
    """renders an evaluation batch"""

    # init and checks
    eb = get_object_or_404(EvaluationBatch.objects.all(), id=ebid)
    eb_form = None
    if not eb.is_accessible(request.user):
        messages.error(
            request, 'You are not allowed to view this Evaluation Batch.')
        redirect('e_list')

    # post request
    if request.method == 'POST':
        if 'eb_switch' in request.POST:
            if eb.added_by == request.user:
                eb.switch()
                messages.success(request, 'switch successful!')
        elif 'restart' in request.POST:
            eid = request.POST.get('restart_eid', None)
            if eid:
                start_eval(eid)
                Evaluation.objects.get(id=eid).clear_results()
                messages.info(request, 'Evalulation is been restarted!')
            else:
                messages.error(request, 'Evalulation restart failed!')
        elif 'eb_edit' in request.POST:
            eb_form = EvalBatchEditForm(instance=eb)
            if eb_form.is_valid():
                eb_form.save()
                messages.success(request, 'edit successfull')
            else:
                messages.error(request, 'edit failed')

    # response
    return {'eb': eb,
            'eb_form': eb_form or EvalBatchEditForm()}


@render_to('spike_eval/evaluation/algo_detail.html')
def adetail(request, aid):
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


@render_to('spike_eval/evaluation/algo_list.html')
def alist(request):
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


def dl_zip(request, ebid):
    # init and checks
    eb = get_object_or_404(EvaluationBatch.objects.all(), id=ebid)
    e_list = [e for e in eb.evaluation_set.order_by('trial__parameter')]
    arc, arc_buf, buf = None, None, None

    # build archive
    try:
        # build buffer and archive
        arc_buf = StringIO()
        arc = zipfile.ZipFile(arc_buf, mode='w')

        # write introduction | TODO: add a proper README file
        arc.writestr('README', "RESULTS FOR %s\n\nsome explanation should go here!\n" % (str(eb)))

        # write evaluations
        for e in e_list:
            e_name = slugify(e.trial.name)
            buf = StringIO()
            for r in e.eval_res:
                buf.write('%s\n' % ','.join(map(str, r.display())))
            buf.seek(0)
            arc.writestr('%s/tbl.csv' % e_name, buf.read())
            buf.close()
            for ri in e.eval_res_img:
                arc.writestr(
                    '%s/img_%s.%s' % (e_name, ri.img_type, ri.img_data.path.split('.')[-1]),
                    ri.img_data.read())
        arc.close()
        arc_buf.seek(0)

        # send response
        response = HttpResponse(arc_buf.read())
        response['Content-Disposition'] = 'attachment; filename=%s.zip' % slugify(str(eb))
        response['Content-Type'] = 'application/x-zip'
        return response
    except Exception, ex:
        print ex
        return redirect(eb)
    finally:
        try:
            arc.close()
            del arc
        except:
            pass
        try:
            arc_buf.close()
            del arc_buf
        except:
            pass
        try:
            buf.close()
            del buf
        except:
            pass

##---MAIN

if __name__ == '__main__':
    pass
