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


##---TESTS

class TestImports(unittest.TestCase):
    """test case for package imports"""

    def test_scipy(self):
        import scipy

        self.assertGreaterEqual(scipy.__version__, '0.6')

    def test_mdp(self):
        import mdp

        self.assertGreaterEqual(mdp.__version__, '2.3')

    def test_matplotlib(self):
        import matplotlib

        self.assertGreaterEqual(matplotlib.__version__, '0.98')
        self.assertEqual(matplotlib.validate_backend('agg'), 'agg')

    def test_pil_image(self):
        import Image

        self.assertGreaterEqual(Image.VERSION, '1.1.6')

    def test_tables(self):
        import tables

        self.assertGreaterEqual(tables.__version__, '2.0')

    def test_texttable(self):
        import texttable

        self.assertGreaterEqual(texttable.__version__, '0.8')

##---MAIN

if __name__ == '__main__':
    unittest.main()
