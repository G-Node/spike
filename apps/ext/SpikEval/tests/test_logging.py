# -*- coding: utf-8 -*-
#
# tests - test_logging.py
#
# Philipp Meier - <pmeier82 at gmail dot com>
# 2011-11-01
#

"""unit tests for logging"""
__docformat__ = 'restructuredtext'


##---IMPORTS

try:
    # for python < 2.7.x
    import unittest2 as unittest
except ImportError:
    import unittest

import os
from spikeval.logging import Logger
from StringIO import StringIO


##---TESTS

class TestLogging(unittest.TestCase):
    """test case for logging"""

    def setUp(self):
        self.str_test = ['test1', 'test2', 'test3']

    def test_is_file_like(self):
        self.assertTrue(Logger.is_file_like(StringIO()))
        self.assertFalse(Logger.is_file_like(self))

    def test_logger_file(self):
        fname = os.path.join(os.path.dirname(__file__), 'test_logger.txt')
        if os.path.exists(fname):
            os.remove(fname)
        canvas = open(fname, 'a+')
        logger = Logger.get_logger(canvas)
        logger.log(*self.str_test)
        self.assertEqual(logger.get_content().split(), self.str_test)
        os.remove(fname)

    def test_logger_strio(self):
        canvas = StringIO()
        logger = Logger.get_logger(canvas)
        logger.log(*self.str_test)
        self.assertEqual(logger.get_content().split(), self.str_test)

    def test_delimiter_line(self):
        L = Logger(StringIO())
        L.log_delimiter_line()
        self.assertEqual(L.get_content().strip(), '*' * 20)

##---MAIN

if __name__ == '__main__':
    unittest.main()
