# -*- coding: utf-8 -*-
#
# spikeval - logging.py
#
# Philipp Meier - <pmeier82 at gmail dot com>
# 2011-10-18
#

"""logging class wrapping any object implementing the file interface"""
__docformat__ = 'restructuredtext'
__all__ = ['Logger', 'IFILE_METHODS', 'STDLOG']


##---IMPORTS

from sys import stdout
from StringIO import StringIO


###---CONSTANTS

method_sets = [set(filter(lambda x: not x.startswith('__'),
                          cls.__dict__.keys()))
               for cls in [file, StringIO]]
IFILE_METHODS = method_sets[0]
for method_set in method_sets:
    IFILE_METHODS = IFILE_METHODS.intersection(method_set)
del method_set, method_sets
STDLOG = stdout



##---CLASSES

class Logger(object):
    """logging wrapper"""

    def __init__(self, file_like=STDLOG):
        """
        :type file_like: file-like
        :param file_like: object implementing the file interface
        :raises IOError: if file_like is not compatible
        """

        # inits and checks
        if not self.is_file_like(file_like):
            raise ValueError('file_like must implement the file interface!')
        self._core = file_like

    def __del__(self):
        self._core.flush()
        # XXX: should we close self._core?!

    def __getattr__(self, attr):
        try:
            return getattr(self._core, attr)
        except:
            raise AttributeError("'Logger' has no attribute '%s'" % attr)

    def log(self, *args, **kwargs):
        """log a string to a new line on self._core
        :type args: tuple
        :param args: multiple strings
        :type flush: bool
        :keyword flush: if True, force flush on the file-like object
            Default=False
        :raise IOError: on error interacting thi self._core
        """

        self._core.write('\n'.join(args) + '\n')
        if kwargs.get('flush', False) is True:
            self._core.flush()

    def log_delimiter_line(self, amount=20, char='*', **kwargs):
        """by default logs a line of 20 stars ('*')
        :type amount: int
        :param amount: amount of chars to print
        :type char: char
        :param char: character to use for the delimiter line
        """

        self.log(char * amount, **kwargs)

    def get_content(self):
        """return the whole content of the current logger"""

        self._core.seek(0)
        return self._core.read()

    @staticmethod
    def is_file_like(obj):
        """check if obj implements the file interface"""

        if len(IFILE_METHODS) == 0:
            return False
        return all([hasattr(obj, method) for method in IFILE_METHODS])

    @staticmethod
    def get_logger(obj):
        """produce Logger from obj, return obj if it is a Logger already

        :type obj: Logger or file_like
        :param obj: object to turn into a Logger
        :raise ValueError: if obj is not implementing the file interface
        """

        if isinstance(obj, Logger):
            return obj
        else:
            return Logger(obj)

##--- MAIN

if __name__ == '__main__':
    pass
