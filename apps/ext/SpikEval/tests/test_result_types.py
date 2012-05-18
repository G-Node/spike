# -*- coding: utf-8 -*-
#
# tests - test_module.py
#
# Philipp Meier - <pmeier82 at gmail dot com>
# 2011-10-11
#

"""unit tests for packages and environment"""
__docformat__ = 'restructuredtext'


##---IMPORTS

try:
    # for python < 2.7.x
    import unittest2 as unittest
except ImportError:
    import unittest

import scipy as sp
import Image
import spikeplot
from spikeval.module.result_types import *


##---TESTS

class TestResultTypes(unittest.TestCase):
    """test case for package imports"""

    def test_mr_string(self):
        data = 'teststr'
        data_res = MRString(data)
        self.assertEqual(data_res.value, data)
        self.assertEqual(data_res.__str__(), 'MRString{%s}' % data)
        self.assertIsInstance(data_res.value, str)

    def test_mr_scalar(self):
        data = 666.666
        data_res = MRScalar(data)
        self.assertEqual(data_res.value, data)
        self.assertEqual(data_res.__str__(), 'MRScalar{%s}' % data)
        self.assertIsInstance(data_res.value, sp.ndarray)

    def test_mr_table(self):
        data = sp.arange(16).reshape(4, 4)
        data_res = MRTable(data)
        data_res_str = """MRTable{
+----+----+----+----+
| 0  | 1  | 2  | 3  |
+----+----+----+----+
| 4  | 5  | 6  | 7  |
+----+----+----+----+
| 8  | 9  | 10 | 11 |
+----+----+----+----+
| 12 | 13 | 14 | 15 |
+----+----+----+----+
}"""
        self.assertTrue(sp.allclose(data_res.value, data))
        self.assertEqual(data_res.__str__(), data_res_str)
        self.assertIsInstance(data_res.value, sp.ndarray)

    def test_mr_dict(self):
        data = dict(zip(range(5), range(5)))
        data_res = MRDict(data)
        data_res_str = """MRDict{
+-----+-------+
| Key | Value |
+=====+=======+
| 0   | 0     |
+-----+-------+
| 1   | 1     |
+-----+-------+
| 2   | 2     |
+-----+-------+
| 3   | 3     |
+-----+-------+
| 4   | 4     |
+-----+-------+
}"""
        self.assertEqual(data_res.value, data)
        self.assertEqual(data_res.__str__(), data_res_str)
        self.assertIsInstance(data_res.value, dict)

    def test_mr_plot(self):
        data1 = sp.array([sp.eye(10), sp.eye(10), sp.eye(10)]).T
        data1_res = MRPlot(data1)
        data2 = Image.frombuffer('RGB', data1.shape[:2], data1, 'raw',
                                 'RGB', 0, 1)
        data2_res = MRPlot(data2)
        data3 = spikeplot.plt.imshow(sp.eye(10)).get_figure()
        data3_res = MRPlot(data3)

        self.assertEqual(data1_res.__str__(), 'MRPlot{Image(10, 10)}')
        self.assertEqual(data2_res.__str__(), 'MRPlot{Image(10, 10)}')
        self.assertEqual(data3_res.__str__(), 'MRPlot{Image(640, 480)}')

        self.assertIsInstance(data1_res.value, Image.Image)
        self.assertIsInstance(data2_res.value, Image.Image)
        self.assertIsInstance(data3_res.value, Image.Image)

##---MAIN

if __name__ == '__main__':
    unittest.main()
