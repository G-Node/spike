# -*- coding: utf-8 -*-
#
# spikeval - module.__init__.py
#
# Philipp Meier <pmeier82 at googlemail dot com>
# 2011-09-29
#

"""modules for evaluation"""
__docformat__ = 'restructuredtext'



##---IMPORTS

from .base_module import BaseModule, ModuleInputError, ModuleExecutionError
from .result_types import (ResultError, ModuleResult, MRString, MRScalar,
                           MRTable, MRDict, MRPlot)

from .mod_plot_data import ModDataPlot
from .mod_metric_alignment import ModMetricAlignment


##---MODULES

MODULES = [ModDataPlot, ModMetricAlignment]
