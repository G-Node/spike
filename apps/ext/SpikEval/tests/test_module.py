# -*- coding: utf-8 -*-
#
# tests - test_module.py
#
# Philipp Meier - <pmeier82 at gmail dot com>
# 2011-10-11
#

"""unit tests for modules"""
__docformat__ = 'restructuredtext'

##---IMPORTS

try:
    # for python < 2.7.x
    import unittest2 as unittest
except ImportError:
    import unittest

import sys
import scipy as sp
from spikeval.module import ModDataPlot, ModMetricAlignment

##---TESTS

class TestModule(unittest.TestCase):
    """test case for package imports"""

    def setUp(self):
        """setup input data"""

        self.raw_data = sp.randn(1000, 4)
        self.sts_gt = {0:sp.array(range(100, 1000, 100)),
                       1:sp.array(range(20, 1000, 100)),
                       3:sp.array([222, 444, 666, 888])}
        shift = 20
        self.sts_ev = {0:sp.array(range(100, 1000, 100)) + shift,
                       1:sp.array(range(20, 1000, 100)) + shift,
                       3:sp.array([222, 444, 666, 888]) + shift}

    def test_mod_data_plots(self):
        mod = ModDataPlot(
            self.raw_data,
            self.sts_gt,
            self.sts_ev,
            sys.stdout)
        mod.apply()
        self.assertEqual(mod.status, 'finalised')

    def test_metric_alignment(self):
        mod = ModMetricAlignment(
            self.raw_data,
            self.sts_gt,
            self.sts_ev,
            sys.stdout)
        mod.apply()
        self.assertEqual(mod.status, 'finalised')

##---MAIN

if __name__ == '__main__':
    unittest.main()
