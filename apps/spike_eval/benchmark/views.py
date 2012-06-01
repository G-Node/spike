##---IMPORTS

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy import nan, nanmax, nanmin

from ..forms import (
    BenchmarkForm, TrialForm, EvaluationForm, SupplementaryForm)
from ..util import render_to

##---MODEL-REFS

Benchmark = models.get_model('benchmark', 'benchmark')
Trial = models.get_model('benchmark', 'trial')
Datafile = models.get_model('datafile', 'datafile')

##---VIEWS

#@login_required
@render_to('spike_eval/benchmark/list.html')
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
    b_list = Benchmark.objects.exclude(state__in=[10, 30])
    if request.user.is_authenticated():
        b_list = b_list | Benchmark.objects.filter(
            owner=request.user, state__in=[10, 30])

    # search terms
    search_terms = request.GET.get('search', '')
    if search_terms:
        b_list = (
            b_list.filter(name__icontains=search_terms)
            | b_list.filter(description__icontains=search_terms)
            #| b_list.filter(tags__icontains=search_terms)
            )

    # response
    return {'b_list':b_list,
            'b_form':b_form,
            'search_terms':search_terms}

#@login_required
@render_to('spike_eval/benchmark/detail.html')
def detail(request, bid):
    """renders details of a particular benchmark"""

    # init and checks
    b_form = t_form = e_forms = s_form = None
    b = get_object_or_404(Benchmark.objects.all(), id=bid)
    if not b.is_accessible(request.user):
        return HttpResponseForbidden(
            'You don\'t have rights to view or modify this Benchmark.')
    t_list = b.trial_set.order_by('parameter')
    if request.user != b.owner:
        t_list = filter(lambda x:x.is_validated(), t_list)

    # post request
    if request.method == 'POST':
        action = request.POST.get('action', None)

        # edit & creation
        if request.user == b.owner:
            if action == 'b_edit':
                b_form = BenchmarkForm(request.POST, instance=b)
                if b_form.is_valid():
                    b = b_form.save()
                    messages.info(request, 'Benchmark edit successful!')
                    return redirect(b)
                else:
                    messages.warning(request, 'Benchmark edit failed!')
            elif action == 't_create':
                t_form = TrialForm(request.POST, request.FILES)
                if t_form.is_valid():
                    t = t_form.save(user=request.user, benchmark=b)
                    messages.info(request, 'Trial creation successful: '
                                           '\'%s\'' % t)
                    return redirect(t)
                else:
                    messages.warning(request, 'Trial creation failed!')
            elif action == 's_create':
                s_form = SupplementaryForm(request.POST, request.FILES)
                if s_form.is_valid():
                    s = s_form.save(user=request.user, benchmark=b)
                    messages.info(request, 'Supplementary creation '
                                           'successful: '
                                           '\'%s\'' % s)

        # user submission
        if action == 'e_submit':
            e_forms = []
            for t in t_list:
                e_form = EvaluationForm(request.POST, request.FILES,
                                        prefix='t-%s' % t.id)
                e_forms.append(e_form)
                if e_form.is_valid():
                    e_form.save(user=request.user)
                    messages.info(
                        request, '%s: submission successful' % t.name)
                else:
                    messages.info(request, '%s: no submission' % t.name)


    # build forms
    if not b_form:
        b_form = BenchmarkForm(instance=b)
    if not t_form:
        t_form = TrialForm(pv_label=b.parameter)
    if not s_form:
        s_form = SupplementaryForm()
    if not e_forms:
        e_forms = [EvaluationForm(prefix='t-%s' % t.id) for t in t_list]

    # response
    return {'b':b,
            't_list':t_list,
            'b_form':b_form,
            't_form':t_form,
            's_form':s_form,
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
@render_to('spike_eval/benchmark/summary.html')
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
        r_list = b.trial_set.order_by('parameter')
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
            data[algo][1][plist.index(e.trial.parameter)] = value

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
@render_to('spike_eval/benchmark/trial.html')
def trial(request, tid):
    """renders details of a trial"""

    # init and checks
    t = get_object_or_404(Trial.objects.all(), id=tid)
    if t.benchmark.owner != request.user:
        return HttpResponseForbidden(
            'You don\'t own this benchmark Benchmark!')
    t_form = None

    # post request
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 't_edit':
            t_form = TrialForm(request.POST, instance=t)
            if t_form.is_valid():
                t_form.save()
                messages.success(request, 'Trial edit successful')
            else:
                messages.warning(request, 'Trial edit failed!')
        elif action == 't_delete':
            t.delete()
            messages.success(
                request, 'Trial deleted: %s' % t.name)
            return redirect(t.benchmark)
        elif action == 't_create':
            t_form = TrialForm(request.POST, request.FILES)
            if t_form.is_valid():
                t_new = t_form.save()
                messages.success(
                    request, 'Version creation successful: %s' % t_new.name)
            else:
                messages.warning(
                    request, 'Version creation failed!')

    # create forms
    if not t_form:
        t_form = TrialForm(instance=t)

    # response
    return {'t':t,
            't_form':t_form,
            }

##---MAIN

if __name__ == '__main__':
    pass