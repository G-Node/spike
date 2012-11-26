##---IMPORTS

import zipfile
from StringIO import StringIO
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.defaultfilters import slugify
from ..forms import BatchEditForm
from ..util import render_to

##---MODEL-REFS

Batch = models.get_model('spike', 'batch')
Evaluation = models.get_model('spike', 'evaluation')

##---VIEWS

@render_to('spike/evaluation/list.html')
def list(request, pk=None):
    """renders a list of available batches"""

    # evaluation batch list
    bt_list = Batch.objects.filter(status=Batch.STATUS.public)
    bt_list_self = None
    if request.user.is_authenticated():
        if request.user.is_superuser:
            bt_list = Batch.objects.all()
        bt_list_self = Batch.objects.filter(owner=request.user)

    # filters
    if pk is not None:
        bt_list = bt_list.filter(benchmark=pk)
        if request.user.is_authenticated():
            bt_list_self = bt_list_self.filter(benchmark=pk)

    # search terms
    search_terms = request.GET.get('search', '')
    if search_terms:
        bt_list = (
            bt_list.filter(algorithm__icontains=search_terms) |
            bt_list.filter(description__icontains=search_terms) |
            bt_list.filter(owner__icontains=search_terms) |
            bt_list.filter(benchmark__icontains=search_terms))

    # response
    return {'bt_list': bt_list,
            'bt_list_self': bt_list_self,
            'search_terms': search_terms}


@render_to('spike/evaluation/detail.html')
def detail(request, pk):
    """renders details of a particular batch"""

    # init and checks
    try:
        bt = Batch.objects.get(pk=pk)
        assert bt.is_accessible(request.user), 'insufficient permissions'
    except Exception, ex:
        messages.error(request, 'You are not allowed to view or modify this Batch: %s' % ex)
        return redirect('ev_list')
    bt_form = None

    # post request
    if request.method == 'POST':
        if 'bt_edit' in request.POST:
            bt_form = BatchEditForm(data=request.POST, instance=bt)
            if bt_form.is_valid():
                bt_form.save()
                messages.success(request, 'Batch edit successfull')
            else:
                messages.error(request, 'Batch edit failed')

    # response
    return {'bt': bt,
            'bt_form': bt_form or BatchEditForm(instance=bt)}


@login_required
def toggle(request, pk):
    """toggle status for benchmark"""

    try:
        bt = Batch.objects.get(pk=pk)
        assert bt.is_editable(request.user), 'insufficient permissions'
        bt.toggle()
        messages.info(request, 'Batch "%s" toggled to %s' % (bt, bt.status))
    except Exception, ex:
        messages.error(request, 'Benchmark not toggled: %s' % ex)
    finally:
        return redirect(bt)


@login_required
def delete(request, pk):
    """delete batch"""

    try:
        bt = Batch.objects.get(pk=pk)
        assert bt.is_editable(request.user), 'insufficient permissions'
        Batch.objects.get(pk=pk).delete()
        messages.success(request, 'Batch "%s" deleted' % bt)
    except Exception, ex:
        messages.error(request, 'Benchmark not deleted: %s' % ex)
    finally:
        return redirect('ev_list')


def zip(request, pk):
    # init and checks
    try:
        bt = Batch.objects.get(pk=pk)
        assert bt.is_accessible(request.user), 'insufficient permissions'
    except Exception, ex:
        messages.error(request, 'You are not allowed to view or modify this Batch: %s' % ex)
        return redirect('ev_list')
    ev_list = [ev for ev in bt.evaluation_set.order_by('trial__parameter')]
    arc, arc_buf, buf = None, None, None

    try:
        # build buffer and archive
        arc_buf = StringIO()
        arc = zipfile.ZipFile(arc_buf, mode='w')

        # write introduction | TODO: add a proper README file
        arc.writestr(
            'README',
            '\n'.join([
                'RESULTS FOR: %s\n' % str(bt),
                'This zip archive was downloaded from http://spike.g-node.org.',
                'It contains the results from a spike sorting evaluation made on the benchmark',
                '\n  %s\n' % str(bt.benchmark),
                'with the algorithm',
                '\n  %s\n' % str(bt.algorithm),
                'on',
                '\n  %s\n' % str(bt.created),
                'by',
                '\n  %s\n' % str(bt.owner),
                '']))

        # write evaluations
        for ev in ev_list:
            if not ev.processed():
                continue
            ev_name = slugify(ev.trial.name)
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
            for rs in ev.eval_res:
                buf.write('%s\n' % ','.join(map(str, rs.display())))
            buf.seek(0)
            arc.writestr('%s/tbl.csv' % ev_name, buf.read())
            buf.close()
            for ri in ev.eval_res_img:
                arc.writestr(
                    '%s/img_%s.%s' % (ev_name, ri.img_type, ri.img_data.path.split('.')[-1]),
                    ri.img_data.read())
        arc.close()
        arc_buf.seek(0)

        # send response
        response = HttpResponse(arc_buf.read())
        response['Content-Disposition'] = 'attachment; filename=%s.zip' % slugify(str(bt))
        response['Content-Type'] = 'application/x-zip'
        return response
    except:
        return redirect(bt)
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


@login_required
def run(request, pk, dest=None):
    try:
        ev = Evaluation.objects.get(pk=pk)
        assert ev.batch.is_editable(request.user), 'insufficient permissions'
        ev.run()
        messages.info(request, 'Evaluation run has been scheduled: %s' % ev)
    except Exception, ex:
        messages.error(request, 'Evaluation run not scheduled: %s' % ex)
    finally:
        return redirect(dest or ev.batch)

##---MAIN

if __name__ == '__main__':
    pass
