import datetime
from datetime import timedelta

from django.shortcuts import render_to_response, get_object_or_404
#from django.core.exceptions import ObjectDoesNotExist
#from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
#from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
#from django.db.models import get_app
#from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from experiments.models import Experiment
from datasets.models import RDataset
from datafiles.models import Datafile
from pinax.apps.projects.models import Project
from django.utils.translation import ugettext as _

@login_required
def state_overview(request, template_name="system_dashboard/state_overview.html"):
    if request.user.is_staff:
	# Basic system state values
	user_count = User.objects.all().count()
	file_count = Datafile.objects.all().count()
	dataset_count = RDataset.objects.all().count()
	experiment_count = Experiment.objects.all().count()
	project_count = Project.objects.all().count()
	total_space_used = 0
	for datafile in Datafile.objects.all():
	    total_space_used += datafile.raw_file.size
	total_space = 38000000000 # 38 GB
	tspu_res = round((float(total_space_used)/float(total_space))*100, 2)
	tsp_res = 100.0 - tspu_res
	return render_to_response(template_name, {
	"user_count": user_count,
	"file_count": file_count,
	"dataset_count": dataset_count,
	"experiment_count": experiment_count,
	"project_count": project_count,
	"total_space_used": tspu_res,
	"total_space": tsp_res,
	}, context_instance=RequestContext(request))	
    else:
	raise Http404

@login_required
def object_statistics(request, template_name="system_dashboard/object_statistics.html"):
    if request.user.is_staff:
	today = datetime.date.today()
	prev_month = today.month - 1
	prev_year = today.year
	if prev_month == 0:
	    prev_month = 12
	    prev_year = prev_year - 1
	f_1 = 'last year'
	f_2 = 'last week'
	f_3 = 'last month'
	f_4 = str(today.strftime("%B %Y"))
	f_5 = str(datetime.date(prev_year, prev_month, 1).strftime("%B %Y"))
	res_days, res_day_display, res_project, res_exprt, res_dataset, res_file = [], [], [], [], [], []

	if request.POST.get("fltr"):
	    fltr = request.POST.get("fltr")
	else:
	    fltr = "last week"
	if 'filter_choice' in request.POST:
	    fltr = request.POST.get("filter_choice")

	if fltr == 'last year':
	    for d in xrange(365):
		res_days.insert(0, today - timedelta(days=d))
	elif fltr == 'last week':
	    for d in xrange(7):
		res_days.insert(0, today - timedelta(days=d))
	elif fltr == 'last month':
	    for d in xrange(31):
		res_days.insert(0, today - timedelta(days=d))
	elif fltr == str(today.strftime("%B %Y")):
	    for d in xrange(today.day):
		res_days.insert(0, datetime.date(today.year, today.month, d+1))
	elif fltr == str(datetime.date(prev_year, prev_month, 1).strftime("%B %Y")):
	    for d in xrange((datetime.date(today.year, today.month, 1) - timedelta(days=1)).day):
		res_days.insert(0, datetime.date(prev_year, prev_month, d+1))
	for d in res_days:
	    res_project.append(Project.objects.all().filter(created__year=d.year).filter(created__month=d.month).filter(created__day=d.day).count())
	    res_exprt.append(Experiment.objects.all().filter(date_created__year=d.year).filter(date_created__month=d.month).filter(date_created__day=d.day).count())
    	    res_dataset.append(RDataset.objects.all().filter(date_added__year=d.year).filter(date_added__month=d.month).filter(date_added__day=d.day).count())
	    res_file.append(Datafile.objects.all().filter(date_added__year=d.year).filter(date_added__month=d.month).filter(date_added__day=d.day).count())
	
	if len(res_days) == 12:
	    for i in res_days:
		res_day_display.append(int(i.strftime("%d")))
	else:
	    for i in res_days:
		res_day_display.append(int(i.strftime("%d")))

	return render_to_response(template_name, {
		"res_day_display": res_day_display,
		"res_project": res_project,
		"res_exprt": res_exprt,
		"res_dataset": res_dataset,
		"res_file": res_file,
		"fltr": fltr,
		"f_1": f_1,
		"f_2": f_2,
		"f_3": f_3,
		"f_4": f_4,
		"f_5": f_5,
	}, context_instance=RequestContext(request))	
    else:
	raise Http404

@login_required
def space_usage(request, template_name="system_dashboard/space_usage.html"):
    if request.user.is_staff:
	return render_to_response(template_name, {
	"some_data": 0,
	}, context_instance=RequestContext(request))	
    else:
	raise Http404

