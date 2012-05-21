# -*- coding: utf-8 -*-
#
# spikeval - module.base_module.py
#
# Philipp Meier <pmeier82 at googlemail dot com>
# 2011-09-29
#

"""result types for module results"""
__docformat__ = 'restructuredtext'
__all__ = ['ResultError', 'ModuleResult', 'MRString', 'MRScalar', 'MRTable',
           'MRDict', 'MRPlot']


##---IMPORTS

import scipy as sp
from texttable import Texttable
import Image
import spikeplot


##---CLASSES

class ResultError(ValueError):
    pass


class ModuleResult(object):
    """module result base class

    Module results can be arbitrarily complex, none the less they can be
    represented as a composition of results from a finite set of result
    types. Each result type implements this interface and provides methods
    to presented itself in various forms.
    """

    BASE = object

    def __init__(self):
        self._value = None

    def __str__(self):
        s = self._str_val().splitlines()
        return '%s{%s%s%s}' % (self.__class__.__name__,
                               '\n' if len(s) > 1 else '',
                               '\n'.join(s),
                               '\n' if len(s) > 1 else '')

    def _str_val(self):
        return str(self._value)

    @property
    def value(self):
        return self._value


class MRString(ModuleResult):
    """single string result"""

    def __init__(self, value):
        """
        :type value: str
        :param value: string value
        """

        if not isinstance(value, str):
            raise ValueError('%s is not a string!' % value)
        self._value = str(value)


class MRScalar(ModuleResult):
    """single value (scalar) result"""

    def __init__(self, value):
        """
        :type value: scalar dtype
        :param value: single digit value
        """

        value_ = value
        if sp.isscalar(value_):
            value_ = sp.asanyarray(value_)
        try:
            assert value_.ndim == 0
        except:
            raise ValueError('%s is not a scalar!' % value)
        self._value = value_


class MRTable(ModuleResult):
    """two dimensional table/matrix result"""

    BASE = sp.ndarray

    def __init__(self, value, header=None):
        """
        :type value: ndarray
        :param value: single digit _value
        :type header: list
        :param header: list of str with as many entries as columns in _value
        """

        val = sp.asanyarray(value)
        if val.dtype == object:
            raise ValueError('%s is not a compatible type: %s' %
                             (value, value.__class__.__name__))
        if val.ndim != 2:
            raise ValueError('%s is not ndim==2: _value.ndim==%s' % val.ndim)
        self._value = val
        self.header = None
        if header is not None:
            if len(header) == self._value.shape[1]:
                self.header = map(str, header)

    @property
    def shape(self):
        return self._value.shape

    def _str_val(self):
        tt = Texttable()
        if self.header is not None:
            tt.header(self.header)
        tt.add_rows(self._value, header=False)
        return tt.draw()


class MRDict(ModuleResult):
    """dictionary result"""

    BASE = dict

    def __init__(self, init_values):
        """
        :type init_values: list
        :param init_values: list of tuples to initialise a dictionary from
        """

        self._value = dict(init_values)

    @property
    def shape(self):
        return self._value.shape

    def _str_val(self):
        tt = Texttable()
        tt.header(['Key', 'Value'])
        tt.add_rows(self._value.items(), header=False)
        return tt.draw()


class MRPlot(ModuleResult):
    """plot result, stored as PIL :Image:"""

    BASE = Image.Image

    def __init__(self, input_data):
        """
        :type input_data: matplotlib.Figure or Image or ndarray
        :param input_data: the input data to generate the :Image: instance
            from.
        """

        is_mpl = isinstance(input_data, spikeplot.plt.Figure)
        is_img = isinstance(input_data, Image.Image)
        is_nda = isinstance(input_data, sp.ndarray)
        if not (is_mpl ^ is_img ^ is_nda):
            raise TypeError('input_data must one of mpl.Figure, Image '
                            'or sp.ndarray')
        im = None
        if is_img:
            im = input_data
        elif is_mpl:
            im = MRPlot.img_from_fig(input_data)
        elif is_nda:
            im = MRPlot.img_from_rgb(input_data)
        else:
            raise ResultError('unrecognized image format!')
        self._value = im

    def _str_val(self):
        return 'Image%s' % str(self.value.size)

    @staticmethod
    def img_from_rgb(rgb):
        """produce :Image: instance from 'RGB' ndarray

        :type rgb: ndarray
        :param rgb: ndarray with shape x,y,3 for rgb or x,y,4 for rgba
            mode
        :return: :Image: instance of the :rgb:
        """

        if not isinstance(rgb, sp.ndarray):
            raise TypeError('rgb must be an sp.ndarray')
        if rgb.ndim != 3:
            raise ValueError('rgb.ndim !=3')
        if rgb.shape[2] != 3:
            raise ValueError('rgb.shape[2] != 3')
        return Image.frombuffer('RGB', rgb.shape[:2], rgb, 'raw', 'RGB', 0, 1)

    @staticmethod
    def img_from_fig(fig):
        """produce :Image: instance from :fig:

        :type fig: matplotlib.pyplot.Figure
        :param fig: input :Figure: instance
        :return: :Image: instance of the canvas of :fig:
        """

        if not isinstance(fig, spikeplot.plt.Figure):
            raise TypeError('fig must be a mpl.Figure')
        fig.canvas.draw()
        rgb = fig.canvas.tostring_rgb()
        rgb = sp.fromstring(rgb, dtype=sp.uint8)
        rgb.shape = map(int, fig.bbox.bounds[2:]) + [3]
        return MRPlot.img_from_rgb(rgb)

##---MAIN

if __name__ == '__main__':
    pass
