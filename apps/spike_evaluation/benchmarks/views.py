##---IMPORTS

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy import nan, nanmax, nanmin

from helpers import render_to
from benchmarks.forms import (
    BenchmarkForm, RecordForm, VersionForm, EvaluationForm)

##---MODEL-REFS

#from benchmarks.models import Benchmark, Record
Benchmark = models.get_model('benchmarks', 'benchmark')
Record = models.get_model('benchmarks', 'record')
#from dfiles.models import Version
Version = models.get_model('dfiles', 'version')

##---VIEWS

#@login_required
@render_to('spike_evaluation/benchmarks/list.html')
def list(request):
    """renders a list of available benchmarks"""

    # post request -> create benchmark
    if request.method == 'POST':
        b_form = BenchmarkForm(request.POST)
        if b_form.is_valid():
            b = b_form.save(user=request.user)
            messages.info(
                request,
                'Benchmark successfully created: \'%s\'' % b.name)
            return redirect(b)
        else:
            messages.warning(
                request,
                'Benchmark creation failed!')

    # get request
    else:
        b_form = BenchmarkForm()

    # benchmark list
    b_list = Benchmark.objects.exclude(state__in=['N', 'C'])
    if request.user.is_authenticated():
        b_list = b_list | Benchmark.objects.filter(owner=request.user,
                                                   state__in=['N', 'C'])

    # search terms
    search_terms = request.GET.get('search', '')
    if search_terms:
        b_list = (
            b_list.filter(name__icontains=search_terms) |
            b_list.filter(description__icontains=search_terms) |
            b_list.filter(tags__icontains=search_terms))

    # response
    return {'b_list':b_list,
            'b_form':b_form,
            'search_terms':search_terms}

#@login_required
@render_to('spike_evaluation/benchmarks/detail.html')
def detail(request, bid):
    """renders details of a particular benchmark"""

    # inits and checks
    b_form = r_form = e_forms = None
    b = get_object_or_404(Benchmark.objects.all(), id=bid)
    if not b.is_accessible(request.user):
        return HttpResponseForbidden(
            'You don\'t have rights to view or modify this Benchmark.')
    r_list = b.record_set.order_by('parameter_value')
    if request.user != b.owner:
        r_list = filter(lambda x:x.ever_validated(), r_list)

    # post request
    if request.method == 'POST':
        action = request.POST.get('action', None)

        # edit & creation
        if request.user == b.owner:
            if action == 'b_edit':
                b_form = BenchmarkForm(request.POST, instance=b)
                if b_form.is_valid():
                    b = b_form.save()
                    messages.info(request, 'Benchmark successfully edited.')
                    return redirect(b)
                else:
                    messages.warning(request, 'Benchmark edit failed!')
            elif action == 'r_create':
                r_form = RecordForm(request.POST, request.FILES)
                if r_form.is_valid():
                    r = r_form.save(user=request.user, benchmark=b)
                    messages.info(
                        request,
                        'Record successfully created: \'%s\'' % r)
                    return redirect(r)
                else:
                    messages.warning(request, 'Record creation failed!')

        # user submission
        if action == 'e_submit':
            #rids = [k.split('-')[1] for k in request.POST.keys()
            #        if k.startswith('r-')]
            #rids = unique(map(int, rids)).tolist()
            e_forms = []
            for r in r_list:
                e_form = EvaluationForm(request.POST,
                                        request.FILES,
                                        prefix='r-%s' % r.id)
                e_forms.append(e_form)
                if e_form.is_valid():
                    e_form.save(user=request.user)
                    messages.info(
                        request, '%s: submission successful' % r.name)
                else:
                    messages.info(request, '%s: no submission' % r.name)


    # build forms
    if not b_form:
        b_form = BenchmarkForm(instance=b)
    if not r_form:
        r_form = RecordForm(pv_label=b.parameter_desc)
    if not e_forms:
        e_forms = [EvaluationForm(prefix='r-%s' % r.id) for r in r_list]

    # response
    return {'b':b,
            'r_list':r_list,
            'b_form':b_form,
            'r_form':r_form,
            'e_forms':e_forms}


@login_required
def archive(request, bid):
    """archives a benchmark"""

    # inits and checks
    b = get_object_or_404(Benchmark.objects.all(), id=bid)
    if b.owner != request.user:
        return HttpResponseForbidden(
            'You don\'t have rights to delete this Benchmark.')

    # archive and redirect
    b.archive()
    messages.info(request, 'Benchmark archived: %s' % b.name)
    return redirect('b_list')


@login_required
def resurrect(request, bid):
    """resurrects a benchmark"""

    # inits and checks
    b = get_object_or_404(Benchmark.objects.all(), id=bid)
    if not b.owner == request.user:
        return HttpResponseForbidden(
            'You don\'t have rights to delete this Benchmark.')

    # resurrect and redirect
    b.resurrect()
    messages.info(request, 'Benchmark resurrected: %s' % b.name)
    return redirect('b_list')

#@login_required
@render_to('spike_evaluation/benchmarks/summary.html')
def summary(request, bid):
    """summary page for benchmark"""

    b = get_object_or_404(Benchmark.objects.all(), id=bid)
    e_list = b.evaluations(pub_state=1)
    if request.user.is_authenticated():
        e_list = e_list | b.evaluations(
            pub_state=0).filter(owner=request.user)

    return {'b':b,
            'e_list':e_list}

#@login_required
def summary_plot(request, bid):
    """generate a plot of the benchmark summary"""
    try:
        # get data
        b = get_object_or_404(Benchmark.objects.all(), id=bid)
        r_list = b.record_set.order_by('parameter_value')
        e_list = b.evaluations()
        plist = [r.parameter_value for r in r_list]
        nparams = len(plist)

        # build data
        data = {}
        for e in e_list:
            algo = e.algorithm
            if not algo:
                algo = 'unknown'
            if algo not in data:
                data[algo] = (plist, [nan] * nparams)
            est = e.summary_table()
            value = est['FN'] + est['FP'] + est['FPAE']
            data[algo][1][plist.index(e.record().parameter_value)] = value

        # build figure
        fig = Figure(edgecolor='white', facecolor='white')
        ax = fig.add_subplot(111)

        # plot content
        ymax = -1
        for algo in data:
            x, y = data[algo]
            ymax = max(ymax, nanmax(y))
            ax.plot(x, y, 'o-', label=algo)

        # beautify
        ax.set_xlabel(b.parameter_desc)
        ax.set_ylabel('errors (FP+FN)')
        ax.legend()
        ax.grid()
        y_margin = ymax * 0.1
        ax.set_ylim(-y_margin, ymax + y_margin)
        x_margin = (nanmax(plist) - nanmin(plist)) * 0.1
        ax.set_xlim(nanmin(plist) - x_margin, nanmax(plist) + x_margin)
        ax.set_xticks(plist)

        # return
        canvas = FigureCanvas(fig)
        response = HttpResponse(content_type='image/png')
        canvas.print_png(response)
    except:
        response = HttpResponse(content_type='image/png')
        import sys, traceback

        traceback.print_exception(*sys.exc_info())
        sys.exc_clear()
    finally:
        return response


@login_required
@render_to('spike_evaluation/benchmarks/record.html')
def record(request, rid):
    """renders a list of versions of a particular file"""

    # inits and checks
    r = get_object_or_404(Record.objects.all(), id=rid)
    if r.benchmark.owner != request.user:
        return HttpResponseForbidden(
            'You don\'t have rights to delete this Benchmark.')
    r_form = v_form = None

    # post request
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'r_edit':
            r_form = RecordForm(request.POST, instance=r)
            if r_form.is_valid():
                r_form.save()
                messages.info(request, 'Record successfully edited')
            else:
                messages.warning(request, 'Record edit failed!')
        elif action == 'r_delete':
            r.delete()
            messages.info(
                request, 'Record deleted: %s' % r.name)
            return redirect(r.benchmark)
        elif action == 'v_create':
            v_old_id = request.POST.get('vid')
            print v_old_id
            v_old = get_object_or_404(Version.objects.all(), id=v_old_id)
            v_form = VersionForm(request.POST, request.FILES, instance=v_old)
            if v_form.is_valid():
                v_new = v_form.save()
                messages.info(
                    request, 'Version successfully created: %s' % v_new.name)
            else:
                messages.info(
                    request, 'Version creation failed!')

    # create forms
    if not r_form:
        r_form = RecordForm(instance=r)
    if not v_form:
        v_form = VersionForm()

    # response
    return {'r':r,
            'r_form':r_form,
            'v_form':v_form}

##---MAIN

if __name__ == '__main__':
    pass
