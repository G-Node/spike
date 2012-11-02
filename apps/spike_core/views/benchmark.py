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

from ..forms import BenchmarkForm, TrialForm, EvaluationSubmitForm, SupplementaryForm
from ..tasks import validate_groundtruth_file, validate_rawdata_file
from ..util import render_to, PLOT_COLORS

##---MODEL-REFS

Benchmark = models.get_model('spike', 'benchmark')
Trial = models.get_model('spike', 'trial')

##---VIEWS

@render_to('spike/benchmark/list.html')
def list(request):
    """renders a list of available benchmarks"""

    # post request
    if request.method == 'POST':
        bm_form = BenchmarkForm(request.POST)
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
def detail(request, bmid):
    """renders details of a particular benchmark"""

    # init and checks
    try:
        bm = Benchmark.objects.get(pk=bmid)
        assert bm.is_accessible(request.user), 'insufficient permissions'
    except Exception, ex:
        messages.error(request, 'You are not allowed to view or modify this Benchmark: %s' % ex)
        return redirect('bm_list')
    bm_form = tr_form = ev_form = sf_form = None
    tr_list = bm.trial_set.order_by('parameter')
    if not bm.is_editable(request.user):
        tr_list = filter(lambda x: x.is_validated(), tr_list)
    sf_list = bm.datafile_set.all()

    # post request
    if request.method == 'POST':
        if bm.is_editable(request.user):
            if 'bm_edit' in request.POST:
                bm_form = BenchmarkForm(request.POST, instance=bm)
                if bm_form.is_valid():
                    bm = bm_form.save()
                    messages.success(request, 'Benchmark edit successful!')
                    return redirect(bm)
                else:
                    messages.error(request, 'Benchmark edit failed!')
            elif 'tr_create' in request.POST:
                tr_form = TrialForm(request.POST, request.FILES)
                if tr_form.is_valid():
                    tr = tr_form.save(user=request.user, benchmark=bm)
                    messages.success(
                        request, 'Trial creation successful: "%s"' % tr)
                    return redirect(tr)
                else:
                    messages.error(request, 'Trial creation failed')
            elif 'sf_create' in request.POST:
                sf_form = SupplementaryForm(request.POST, request.FILES)
                if sf_form.is_valid():
                    sf = sf_form.save(user=request.user, obj=bm)
                    messages.success(request, 'Supplementary creation successful: "%s"' % sf)
                else:
                    messages.error(request, 'Supplementary creation failed!')
            elif 'sf_delete' in request.POST:
                try:
                    sid = int(request.POST['sf_id'])
                    assert bm.is_editable(request.user), 'insufficient permissions'
                    sf = bm.datafile_set.get(pk=sid)
                    sf.delete()
                    messages.success(request, 'Benchmark Supplementary "%s" deleted' % sf)
                except Exception, ex:
                    messages.error(request, 'Benchmark Supplementary not deleted: %s' % ex)

        # user submission
        if 'ev_submit' in request.POST:
            ev_form = EvaluationSubmitForm(
                request.POST, request.FILES, benchmark=bm)
            if ev_form.is_valid():
                ev = ev_form.save(user=request.user)
                messages.success(request, 'Evaluation submission successful')
                return redirect(ev)
            else:
                messages.error(request, 'Evaluation submission failed')

    # build forms
    if not bm_form:
        bm_form = BenchmarkForm(instance=bm)
    if not tr_form:
        tr_form = TrialForm(pv_label=bm.parameter)
    if not sf_form:
        sf_form = SupplementaryForm()
    if not ev_form:
        ev_form = EvaluationSubmitForm(benchmark=bm)

    # response
    return {'bm': bm,
            'sf_list': sf_list,
            'tr_list': tr_list,
            'bm_form': bm_form,
            'ev_form': ev_form,
            'sf_form': sf_form,
            'tr_form': tr_form}


@render_to('spike/benchmark/trial.html')
def trial(request, trid):
    """renders details of a trial"""

    # init and checks
    try:
        tr = Trial.objects.get(pk=trid)
        assert tr.benchmark.is_editable(request.user), 'insufficient permissions!'
    except Exception, ex:
        messages.error(request, 'You are not allowed to view or modify this Trial: %s' % ex)
        return redirect('bm_list')
    tr_form = None

    # post request
    if request.method == 'POST':
        if 'tr_edit' in request.POST:
            tr_form = TrialForm(request.POST, request.FILES, instance=tr)
            if tr_form.is_valid():
                if tr_form.save():
                    messages.success(request, 'Trial edit successful')
                else:
                    messages.info(request, 'No changes detected')
            else:
                messages.error(request, 'Trial edit failed')
        elif 'tr_delete' in request.POST:
            bm = tr.benchmark
            tr.delete()
            messages.success(request, 'Trial "%s" deleted' % tr)
            return redirect(bm)
        elif 'tr_validate' in request.POST:
            try:
                if tr.rd_file:
                    validate_rawdata_file(tr.rd_file.id)
                if tr.gt_file:
                    validate_groundtruth_file(tr.gt_file.id)
            except:
                messages.error(request, 'Trial validation failed')
            else:
                messages.info(request, 'Trial validation scheduled')

    # create forms
    if not tr_form:
        tr_form = TrialForm(instance=tr, pv_label=tr.benchmark.parameter)

    # response
    return {'tr': tr,
            'tr_form': tr_form}


@login_required
def toggle(request, bmid):
    """toggle status for benchmark"""

    try:
        bm = Benchmark.objects.get(pk=bmid)
        assert bm.is_editable(request.user), 'insufficient permissions'
        bm.toggle()
        messages.info(request, 'Benchmark "%s" toggled to %s' % (bm, bm.status))
    except Exception, ex:
        messages.error(request, 'Benchmark not toggled: %s' % ex)
    finally:
        return redirect(bm)


@login_required
def delete(request, bmid):
    """delete benchmark"""

    try:
        bm = Benchmark.objects.get(pk=bmid)
        assert bm.is_editable(request.user), 'insufficient permissions'
        Benchmark.objects.get(pk=bmid).delete()
        messages.success(request, 'Benchmark "%s" deleted' % bm)
    except Exception, ex:
        messages.error(request, 'Benchmark not deleted: %s' % ex)
    finally:
        return redirect('bm_list')


@render_to('spike/benchmark/summary.html')
def summary(request, bmid):
    """summary page for benchmark"""

    b = get_object_or_404(Benchmark.objects.all(), id=bmid)
    eb_list = b.eval_batches(status=20)
    if request.user.is_authenticated():
        eb_list_self = b.eval_batches(status=10)
        if not request.user.is_superuser:
            eb_list_self = eb_list_self.filter(added_by=request.user)
        eb_list |= eb_list_self
    return {'b': b,
            'eb_list': eb_list.order_by('id')}


def summary_plot(request, bmid=None, mode=None, legend=False):
    """generate a plot of the benchmark summary"""

    ## DEBUG
    #print bmid, mode, legend
    ## GUBED

    fig = None
    try:
        # init and checks
        b = get_object_or_404(Benchmark.objects.all(), id=bmid)
        t_list = list(b.trial_set.order_by('parameter'))
        eb_list = b.eval_batches(status=20)
        if request.user.is_authenticated():
            eb_list_self = b.eval_batches(status=10)
            if not request.user.is_superuser:
                eb_list_self = eb_list_self.filter(added_by=request.user)
            eb_list |= eb_list_self
        eb_list.order_by('id')
        param_labels = [t.parameter for t in t_list]
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
        for eb in eb_list:
            y_curve = [nan] * np
            for e in eb.evaluation_set.all():
                try:
                    y_curve[t_list.index(e.trial)] = e.summary_table()[mode]
                except:
                    pass
            if nansum(y_curve) >= 0:
                # TODO: fix "empty" evaluation batches!!
                y_max = nanmax(y_curve + [y_max])
                #y_curve = map(lambda x: x + 1.0, y_curve)
                #ax.semilogy(y_curve, 'o-', label='EB #%s' % eb.id)
                ax.plot(y_curve, 'o-', label='EB #%s' % eb.id)

        # beautify Y-axis
        ax.set_ylabel('Error Count')
        y_margin = y_max * 0.05
        ax.set_ylim(-y_margin, y_max + y_margin)
        # beautify X-axis
        ax.set_xlabel(b.parameter)
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


def zip(request, bmid):
    # init and checks
    try:
        bm = Benchmark.objects.get(pk=bmid)
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

##---MAIN

if __name__ == '__main__':
    pass
