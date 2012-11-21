##---IMPORTS

import zipfile
from StringIO import StringIO
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.defaultfilters import slugify
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy import nan, nansum, nanmax

from ..forms import BenchmarkForm, TrialForm, BatchSubmitForm, AppendixForm
from ...util import render_to, PLOT_COLORS

##---MODEL-REFS

Benchmark = models.get_model('spike', 'benchmark')
Trial = models.get_model('spike', 'trial')

##---VIEWS

@render_to('spike/benchmark/list.html')
def list(request):
    """renders a list of available benchmarks"""

    # post request
    if request.method == 'POST':
        bm_form = BenchmarkForm(data=request.POST)
        if bm_form.is_valid():
            bm = bm_form.save(user=request.user)
            messages.success(request, 'Benchmark creation successful: "%s"' % bm.name)
            return redirect(bm)
        else:
            messages.error(request, 'Benchmark creation failed')

    # get request
    else:
        bm_form = BenchmarkForm()

    # benchmark list
    bm_list = Benchmark.objects.filter(status=Benchmark.STATUS.public)
    bm_list_self = None
    if request.user.is_authenticated():
        if request.user.is_superuser:
            bm_list = Benchmark.objects.all()
        bm_list_self = Benchmark.objects.filter(owner=request.user)

    # search terms
    search_terms = request.GET.get('search', '')
    if search_terms:
        bm_list = (
            bm_list.filter(name__icontains=search_terms) |
            bm_list.filter(description__icontains=search_terms) |
            bm_list.filter(owner_name__icontains=search_terms))

    # response
    return {'bm_form': bm_form,
            'bm_list': bm_list,
            'bm_list_self': bm_list_self,
            'search_terms': search_terms}


@render_to('spike/benchmark/detail.html')
def detail(request, pk):
    """renders details of a particular benchmark"""

    # init and checks
    try:
        bm = Benchmark.objects.get(pk=pk)
        assert bm.is_accessible(request.user), 'insufficient permissions'
    except Exception, ex:
        messages.error(request, 'You are not allowed to view or modify this Benchmark: %s' % ex)
        return redirect('bm_list')
    bm_form = tr_form = bt_form = ap_form = None
    tr_list = bm.trial_set.order_by('parameter')
    if not bm.is_editable(request.user):
        tr_list = filter(lambda x: x.is_valid, tr_list)

    # post request
    if request.method == 'POST':
        if bm.is_editable(request.user):
            if 'bm_edit' in request.POST:
                bm_form = BenchmarkForm(data=request.POST, instance=bm)
                if bm_form.is_valid():
                    bm = bm_form.save()
                    messages.success(request, 'Benchmark edit successful!')
                    return redirect(bm)
                else:
                    messages.error(request, 'Benchmark edit failed!')
            elif 'tr_create' in request.POST:
                tr_form = TrialForm(data=request.POST, files=request.FILES)
                tr = None
                if tr_form.is_valid():
                    tr = tr_form.save(benchmark=bm)
                if tr is not None:
                    messages.success(
                        request, 'Trial creation successful: "%s"' % tr)
                    return redirect(tr)
                else:
                    messages.error(request, 'Trial creation failed')
            elif 'ap_create' in request.POST:
                ap_form = AppendixForm(data=request.POST, files=request.FILES, obj=bm)
                if ap_form.is_valid():
                    ap = ap_form.save()
                    messages.success(request, 'Appendix creation successful: "%s"' % ap)
                else:
                    messages.error(request, 'Appendix creation failed!')

        # user submission
        if 'ev_submit' in request.POST:
            bt_form = BatchSubmitForm(data=request.POST, files=request.FILES, benchmark=bm)
            if bt_form.is_valid():
                ev = bt_form.save(user=request.user)
                messages.success(request, 'Evaluation submission successful')
                return redirect(ev)
            else:
                messages.error(request, 'Evaluation submission failed')

    # build forms
    if not ap_form:
        ap_form = AppendixForm(obj=bm)
    if not bm_form:
        bm_form = BenchmarkForm(instance=bm)
    if not tr_form:
        tr_form = TrialForm(pv_label=bm.parameter)
    if not bt_form:
        bt_form = BatchSubmitForm(benchmark=bm)

    # response
    return {'bm': bm,
            'appendix': bm.data_set.filter(kind='appendix'),
            'tr_list': tr_list,
            'ap_form': ap_form,
            'bm_form': bm_form,
            'bt_form': bt_form,
            'tr_form': tr_form}


@login_required
def toggle(request, pk):
    """toggle status for benchmark"""

    try:
        bm = Benchmark.objects.get(pk=pk)
        assert bm.is_editable(request.user), 'insufficient permissions'
        bm.toggle()
        messages.info(request, 'Benchmark "%s" toggled to %s' % (bm, bm.status))
    except Exception, ex:
        messages.error(request, 'Benchmark not toggled: %s' % ex)
    finally:
        return redirect(bm)


@login_required
def delete(request, pk):
    """delete benchmark"""

    try:
        bm = Benchmark.objects.get(pk=pk)
        assert bm.is_editable(request.user), 'insufficient permissions'
        Benchmark.objects.get(pk=pk).delete()
        messages.success(request, 'Benchmark "%s" deleted' % bm)
    except Exception, ex:
        messages.error(request, 'Benchmark not deleted: %s' % ex)
    finally:
        return redirect('bm_list')


@render_to('spike/benchmark/summary.html')
def summary(request, pk):
    """summary page for benchmark"""

    try:
        bm = Benchmark.objects.get(pk=pk)
        assert bm.is_accessible(request.user), 'insufficient permissions'
    except Exception, ex:
        messages.error(request, 'You are not allowed to view or modify this Benchmark: %s' % ex)
        return redirect('bm_list')
    bt_list = bm.batch_set.filter(status=Benchmark.STATUS.public)
    if request.user.is_authenticated():
        bt_list_self = bm.batch_set.filter(status=Benchmark.STATUS.private)
        if not request.user.is_superuser:
            bt_list_self = bt_list_self.filter(owner=request.user)
        bt_list |= bt_list_self
    return {'bm': bm,
            'bt_list': bt_list.order_by('id')}


def summary_plot(request, pk=None, mode=None, legend=False):
    """generate a plot of the benchmark summary"""

    ## DEBUG
    print 'pk :: %s(%s)' % (pk.__class__.__name__, pk)
    print 'mode :: %s(%s)' % (mode.__class__.__name__, mode)
    print 'legend :: %s(%s)' % (legend.__class__.__name__, legend)
    ## GUBED

    fig = None
    try:
        # init and checks
        bm = get_object_or_404(Benchmark.objects.all(), id=pk)
        tr_list = bm.trial_set.order_by('parameter')
        bt_list = bm.batch_set.filter(status=Benchmark.STATUS.public)
        if request.user.is_authenticated():
            eb_list_self = bm.batch_set.filter(status=Benchmark.STATUS.private)
            if not request.user.is_superuser:
                eb_list_self = eb_list_self.filter(owner=request.user)
            bt_list |= eb_list_self
        bt_list.order_by('id')
        param_labels = [t.parameter for t in tr_list]
        np = len(param_labels)
        y_max = 1.

        # build figure
        fig = Figure(
            figsize=(5, 5),
            facecolor='white',
            edgecolor='white',
            frameon=False)
        #ax = fig.add_subplot(111)
        ax = fig.add_axes([.15, .1, .8, .8])
        ax.set_color_cycle(PLOT_COLORS)

        # plot data
        if mode is None or (mode is not None and mode not in ['error_sum',
                                                              'FPAEno',
                                                              'FNno',
                                                              'FP',
                                                              'FPAEo',
                                                              'FNo']):
            mode = 'error_sum'
        for bt in bt_list:
            y_curve = [nan] * np
            for ev in bt.evaluation_set.all():
                try:
                    y_curve[tr_list.index(ev.trial)] = ev.summary_table()[mode]
                except:
                    pass
            if nansum(y_curve) >= 0:
                # TODO: fix "empty" evaluation batches!!
                y_max = nanmax(y_curve + [y_max])
                #y_curve = map(lambda x: x + 1.0, y_curve)
                #ax.semilogy(y_curve, 'o-', label='EB #%s' % eb.id)
                ax.plot(y_curve, 'o-', label='EB #%s' % bt.id)

        # beautify Y-axis
        ax.set_ylabel('Error Count')
        y_margin = y_max * 0.05
        ax.set_ylim(-y_margin, y_max + y_margin)
        # beautify X-axis
        ax.set_xlabel(bm.parameter)
        x_margin = np * 0.05
        ax.set_xlim(-x_margin, (1 + .5 * (legend is True)) * np + x_margin - 1)
        ax.set_xticks(range(np))
        ax.set_xticklabels(param_labels)
        # figure title
        title = {
            'error_sum': 'Total Error',
            'FPAEno': 'Classification Error (NO)',
            'FNno': 'False Negative (NO)',
            'FP': 'False Positive (NO)',
            'FPAEo': 'Classification Error (O)',
            'FNo': 'False Negative (O)',
        }.get(mode, 'Total Error')
        ax.set_title(title)
        if legend is True:
            ax.legend(
                loc='upper center',
                ncol=2,
                fancybox=True,
                bbox_to_anchor=(.90, 1),
                numpoints=1,
                prop={'size': 8},
            )
        ax.grid()

        ## DEBUG
        #print 'DPI:', fig.get_dpi(), 'y_max', y_max
        ## GUBED
    except:
        import sys, traceback

        traceback.print_exception(*sys.exc_info())
        sys.exc_clear()
    finally:
        #response = HttpResponse(content_type='image/png')
        response = HttpResponse(content_type='image/svg+xml')
        try:
            canvas = FigureCanvas(fig)
            #canvas.print_png(response)
            canvas.print_svg(response)
        except:
            pass
        return response


def zip(request, pk):
    # init and checks
    try:
        bm = Benchmark.objects.get(pk=pk)
        assert bm.is_accessible(request.user), 'insufficient permissions'
    except Exception, ex:
        messages.error(request, 'You are not allowed to view or modify this Benchmark: %s' % ex)
        return redirect('ev_list')
    tr_list = [tr for tr in bm.trial_set.order_by('parameter') if tr.is_validated()]
    arc, buf = None, None

    # build archive
    try:
        # build buffer and archive
        buf = StringIO()
        arc = zipfile.ZipFile(buf, mode='w')
        for tr in tr_list:
            arc.writestr(tr.rd_file.name, tr.rd_file.file.read())
            if bm.gt_access == 20 and tr.gt_file:
                arc.writestr(tr.gt_file.name, tr.gt_file.file.read())
        arc.close()
        buf.seek(0)

        response = HttpResponse(buf.read())
        response['Content-Disposition'] = 'attachment; filename=%s.zip' % slugify(bm.name)
        response['Content-Type'] = 'application/x-zip'
        return response
    except:
        return redirect(bm)
    finally:
        try:
            del arc
        except:
            pass
        try:
            del buf
        except:
            pass


@render_to('spike/benchmark/trial.html')
def trial(request, pk):
    """renders details of a trial"""

    # init and checks
    try:
        tr = Trial.objects.get(pk=pk)
        assert tr.benchmark.is_editable(request.user), 'insufficient permissions!'
    except Exception, ex:
        messages.error(request, 'You are not allowed to view or modify this Trial: %s' % ex)
        return redirect('bm_list')
    tr_form = None

    # post request
    if request.method == 'POST':
        if 'tr_edit' in request.POST:
            tr_form = TrialForm(data=request.POST, files=request.FILES, instance=tr)
            if tr_form.is_valid():
                if tr_form.save():
                    messages.success(request, 'Trial edit successful')
                else:
                    messages.info(request, 'No changes detected')
            else:
                messages.error(request, 'Trial edit failed')

    # create forms
    if not tr_form:
        tr_form = TrialForm(instance=tr, pv_label=tr.benchmark.parameter)

    # response
    return {'tr': tr,
            'tr_form': tr_form}


@login_required
def trial_delete(request, pk, dest=None):
    """delete trial"""

    try:
        tr = Trial.objects.get(pk=pk)
        assert tr.benchmark.is_editable(request.user), 'insufficient permissions'
        Trial.objects.get(pk=pk).delete()
        messages.success(request, 'Trial "%s" deleted' % tr)
    except Exception, ex:
        messages.error(request, 'Trial not deleted: %s' % ex)
    finally:
        return redirect(dest or tr.benchmark)


@login_required
def trial_validate(request, pk, dest=None):
    try:
        tr = Trial.objects.get(pk=pk)
        assert tr.benchmark.is_editable(request.user), 'insufficient permissions'
        tr.validate()
        messages.info(request, 'Validation run has been scheduled: %s' % tr)
    except Exception, ex:
        messages.error(request, 'Validation run not scheduled: %s' % ex)
    finally:
        return redirect(dest or tr)

##---MAIN

if __name__ == '__main__':
    pass
