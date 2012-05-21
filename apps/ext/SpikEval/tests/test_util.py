# -*- coding: utf-8 -*-
#
# tests - test_imports.py
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
from spikeval.util import *


##---TESTS

class TestUtil(unittest.TestCase):
    """test case for utility functions"""

    def test_dict_list2arr(self):
        inp = {0:range(10)}
        self.assertIsInstance(inp[0], list)
        inp = dict_list2arr(inp)
        self.assertIsInstance(inp[0], sp.ndarray)

    def test_dict_arrsort(self):
        inp = {0:sp.random.randint(0, 100, 10)}
        inp = dict_arrsort(inp)
        self.assertTrue(all(sp.diff(inp[0]) >= 0))

    def test_extract_spikes(self):
        inp = sp.randn(1000, 2)
        eps = sp.array([[10, 20], [50, 60]])
        for ep in eps:
            inp[ep[0]:ep[1]] = 0
        out = extract_spikes(inp, eps)
        self.assertTrue((out == 0).all())

    def test_jitter_st(self):
        start, end, jitter = 0, 100000, 5
        st_init = sp.random.randint(start, end, 20)
        st_init.sort()
        st_jitt = jitter_st(st_init, jitter, start, end)
        self.assertTrue(
            (sp.absolute(st_init - st_jitt) <= jitter).all())

    def test_jitter_sts(self):
        start, end, jitter = 0, 100000, 5
        st_init0 = sp.random.randint(start, end, 20)
        st_init0.sort()
        st_init1 = sp.random.randint(start, end, 20)
        st_init1.sort()
        sts_init = {0:st_init0, 1:st_init1}
        sts_jitt = jitter_sts(sts_init, jitter, start, end)
        for k in sts_jitt:
            self.assertTrue(
                (sp.absolute(sts_init[k] - sts_jitt[k]) <= jitter).all())

    def test_matrix_argmax(self):
        M = sp.array([[1, 2], [3, 4]])
        self.assertEqual((1, 1), matrix_argmax(M))

    def test_matrix_argmin(self):
        M = sp.array([[1, 2], [3, 4]])
        self.assertEqual((0, 0), matrix_argmin(M))

    def test_sortrows(self):
        dim = 100, 3
        data = sp.random.randint(0, 100, dim[0] * dim[1]).reshape(*dim)
        data_sorted = sortrows(data)
        last_row = [0]*dim[1]
        for row in data_sorted:
            for i in xrange(dim[1]-1):
                self.assertGreaterEqual(row[i], last_row[i])
                if row[i] > last_row[i]:
                    break
            last_row = row

##---MAIN

if __name__ == '__main__':
    unittest.main()
