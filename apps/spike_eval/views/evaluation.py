##---IMPORTS

import zipfile
from StringIO import StringIO
from django.contrib import messages
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.defaultfilters import slugify
from ..forms import EvalBatchEditForm
from ..tasks import start_evaluation
from ..util import render_to

##---MODELREFS

Evaluation = models.get_model('spike_eval', 'evaluation')
EvaluationBatch = models.get_model('spike_eval', 'evaluationbatch')

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
def e_list(request, bid=None):
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
        if request.user.is_authenticated():
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
def e_batch(request, ebid):
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
                start_evaluation(eid)
                Evaluation.objects.get(id=eid).clear_results()
                messages.info(request, 'Evalulation is been restarted!')
            else:
                messages.error(request, 'Evalulation restart failed!')
        elif 'eb_edit' in request.POST:
            eb_form = EvalBatchEditForm(request.POST, instance=eb)
            if eb_form.is_valid():
                eb_form.save()
                messages.success(request, 'edit successfull')
            else:
                messages.error(request, 'edit failed')

    # response
    return {'eb': eb,
            'eb_form': eb_form or EvalBatchEditForm(instance=eb)}


def e_zip(request, ebid):
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
        arc.writestr(
            'README',
            '\n'.join([
                'RESULTS FOR: %s\n' % str(eb),
                'This zip archive was downloaded from http://spike.g-node.org.',
                'It contains the results from a spike sorting evaluation made on the benchmark',
                '\n  %s\n' % str(eb.benchmark),
                'with the algorithm',
                '\n  %s\n' % str(eb.algorithm),
                'on',
                '\n  %s\n' % str(eb.date_created),
                'by',
                '\n  %s\n' % str(eb.added_by),
                '']))

        # write evaluations
        for e in e_list:
            if not e.processed():
                continue
            e_name = slugify(e.trial.name)
            buf = StringIO()
            buf.write(','.join([
                'GT Unit Name',
                'Assigned Sorted Unit',
                'GT Spikes',
                'GT NO',
                'GT Overlaps',
                'Sorted Spikes',
                'Sorted NO',
                'Sorted O',
                'FP(assigned NO from other GT unit)',
                'FP(assigned O from other GT unit)',
                'FP noise',
                'FN(NO detected by other sorted unit)',
                'FN(O det by other unit)',
                'FN(NO not detected)',
                'FN(O not detected)']) + '\n')
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
