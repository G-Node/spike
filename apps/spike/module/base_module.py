# -*- coding: utf-8 -*-
#
# spikeval - module.base_module.py
#
# Philipp Meier <pmeier82 at googlemail dot com>
# 2011-09-29
#

"""module base class for implementing evaluation modules"""
__docformat__ = 'restructuredtext'
__all__ = ['BaseModule', 'ModuleInputError', 'ModuleExecutionError']

##---class

class ModuleInputError(ValueError):
    pass


class ModuleExecutionError(RuntimeError):
    pass


class BaseModule(object):
    """base class for modules

    An evaluation module is a self-contained evaluation step,
    like the application of a single metric or the generation of plots.

    All modules must implement this interface to work in the evaluation
    framework! To implement a new module, subclass BaseModule, implement all
        :self._check_*: methods and set the :RESULT_TYPES: as a list of

    :self._check_raw_data: validates the raw data, and should raise an
        ModuleInputError if the raw data does not validate
    :self._check_sts: validates a spike train set, and should raise an
        ModuleInputError if the raw data does not validate
    :self._check_parameters; checks the optional parameters and should
        return a dict containing all optional parameters initialised to
        their default values or set to the passed values.
    :self._apply: is the execution content of the module and should implement
        the module and store any results in :self.result:.

    You may log any useful information using :self.logger:,
    which is a :Logger: instance.
    """

    def __init__(self, raw_data, sts_gt, sts_ev, **parameters):
        """
        :type raw_data: ndarray or None
        :param raw_data: raw data as ndarray with [samples, channels]
        :type sts_gt: dict
        :param sts_gt: ground truth spike train set
        :type sts_ev: dict
        :param sts_ev: evaluation spike train set
        :keyword: any will be passed as parameter
        """

        # init and checks
        self._stage = 0
        self.parameters = self.check_parameters(parameters)
        self.raw_data = self.check_raw_data(raw_data)
        self.sts_gt = self.check_sts_gt(sts_gt)
        self.sts_ev = self.check_sts_ev(sts_ev)

    @property
    def status(self):
        return {0: 'initialise',
                1: 'processing',
                2: 'finalised'}[self._stage]

    def check_parameters(self, parameters):
        """check parameters

        :type parameters
        :param parameters:
        :return: valid parameters
        """

        return self._check_parameters(parameters)

    def _check_parameters(self, parameters):
        return {}

    def check_raw_data(self, raw_data):
        """check if :raw_data: is valid raw data

        :type raw_data: ndarray
        :param raw_data: raw data
        :raise ModuleInputError: if :raw_data: does not validate
        :return: valid raw data
        """

        return self._check_raw_data(raw_data)

    def _check_raw_data(self, raw_data):
        return None

    def check_sts_gt(self, sts_gt):
        """check if :sts_gt: is a valid ground truth spike train set

        :type sts_gt: dict
        :param sts_gt: ground truth spike train set to validate
        :raise ModuleInputError: if :sts_gt: does not validate
        :return: valid ground truth spike train set
        """

        return self._check_sts_gt(sts_gt)

    def _check_sts_gt(self, sts_gt):
        return None

    def check_sts_ev(self, sts_ev):
        """check if :sts_ev: is a valid evaluation spike train set

        :type sts_ev: dict
        :param sts_ev: evaluation spike train set to validate
        :raise ModuleInputError: if :sts_ev: does not validate
        :return: valid evaluation spike train set
        """

        return self._check_sts_ev(sts_ev)

    def _check_sts_ev(self, sts_ev):
        return None

    def apply(self):
        self._apply()
        self._stage = 2

    def _apply(self):
        raise NotImplementedError

##---MAIN

if __name__ == '__main__':
    pass
