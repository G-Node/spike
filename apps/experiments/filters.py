from django import forms
import datetime

import django_filters as filters

from experiments.models import Experiment

prev_month = datetime.date.today().month - 1
prev_year = datetime.date.today().year
if prev_month == 0:
    prev_month = 12
    prev_year = prev_year - 1
exp_choices = (
    ('1', 'all'),
    ('2', 'last week'),
    ('3', 'last month'),
    ('4', str(datetime.date.today().strftime("%B %Y"))),
    ('5', datetime.date(prev_year, prev_month, 1).strftime("%B %Y"))
)

class ExpFilter(filters.FilterSet):

    state = filters.MultipleChoiceFilter(
        choices = exp_choices,
        widget = forms.CheckboxSelectMultiple,
    )
    
    class Meta:
        model = Experiment
        fields = ["date_created"]