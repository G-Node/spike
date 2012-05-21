# -*- coding: utf-8 -*-
#
# spikeval - util.py
#
# Philipp Meier <pmeier82 at googlemail dot com>
# 2011-09-28
#

"""general utility/tools for dictionary and array handling"""
__docformat__ = 'restructuredtext'
__all__ = ['dict_list2arr', 'dict_arrsort', 'extract_spikes', 'jitter_st',
           'jitter_sts', 'matrix_argmax', 'matrix_argmin', 'sortrows']


##---IMPORTS

import scipy as sp


##---FUNCTIONS

def dict_list2arr(in_dict):
    """converts all lists in a dictionary to `ndarray`. [in place!]

    If there are instances of dict found as values, this function will be
    applied recursively.

    :Parameters:
        in_dict : dict
    """

    try:
        for k in in_dict:
            if isinstance(in_dict[k], list):
                in_dict[k] = sp.asanyarray(in_dict[k])
            elif isinstance(in_dict[k], dict):
                dict_list2arr(in_dict[k])
            else:
                pass
    finally:
        return in_dict


def dict_arrsort(in_dict):
    """sort all arrays in a dictionary ["""

    try:
        for k in in_dict.keys():
            if isinstance(in_dict[k], sp.ndarray):
                in_dict[k] = sp.sort(in_dict[k])
    finally:
        return in_dict


def extract_spikes(data, epochs):
    """extract spike waveforms according to :epochs: from :data:

    :type data: ndarray
    :param data: the signal to extract from [samples, channels]
    :type epochs: ndarray
    :param epochs: epochs to cut [[start,end]], should have common length!
    :type mc: bool
    :returns: ndarray, extracted spike waveforms from :data:
    """

    # inits and checks
    if not all(map(isinstance, [data, epochs], [sp.ndarray] * 2)):
        raise TypeError('pass sp.ndarrays!')
    ns, nc = epochs.shape[0], data.shape[1]
    if epochs.shape[0] == 0:
        return sp.zeros((0, 0))
    tf = epochs[0, 1] - epochs[0, 0]

    # extract
    rval = sp.zeros((ns, tf * nc), dtype=data.dtype)
    for s in xrange(ns):
        for c in xrange(nc):
            correct_beg = min(0, epochs[s, 0])
            correct_end = max(0, epochs[s, 1] - data.shape[0])
            rval[s, c * tf - correct_beg:(c + 1) * tf - correct_end] =\
            data[epochs[s, 0] - correct_beg:epochs[s, 1] - correct_end, c]
    return rval


def jitter_st(st, jitter, start=None, end=None):
    """jitters spike times in :st: by a uniform :jitter:

    :type st: ndarray
    :param st: spike train to jitter
    :type jitter: int
    :param jitter: std parameter for the uniform jitter distribution
    :type start: int
    :param start: if not None: minimum spike time to preserve after jitter
        application.
        Default=None
    :type end: int
    :param end: if not None: maximum spike time to preserve after jitter
        application.
        Default=None
    :returns: ndararay : jittered spike train
    """

    rval = st.copy() + sp.random.uniform(-jitter, jitter, st.size)
    if start is not None:
        rval[rval < start] = start
    if end is not None:
        rval[rval > end] = end
    return rval.astype(int)


def jitter_sts(sts, jitter, start=None, end=None):
    """jitters all spike trains in :sts: w.r.t. uniform distribution from
    [-:jitter: : :jitter:]

    :type sts: dict
    :param sts: spike train set
    :type jitter: int
    :param jitter: jitter parameter for the uniform distribution
    :param start: if not None: minimum spike time to preserve after jitter
        application.
        Default=None
    :type end: int
    :param end: if not None: maximum spike time to preserve after jitter
        application.
        Default=None
    :return: dict : jittered spike train set
    """

    for k, v in sts.items():
        sts[k] = jitter_st(sts[k], jitter, start=start, end=end)
    return sts


def matrix_argmax(M):
    """returns the indices (row,col) of the maximum in M

    :type M: ndarray
    :param M: matrix
    :returns: tuple: indices of the max in M
    """
    idx = sp.nanargmax(M)
    j = int(idx % M.shape[1])
    i = int(sp.floor(idx / M.shape[1]))
    return i, j


def matrix_argmin(M):
    """returns the indices (row,col) of the minimum in M

    :type M: ndarray
    :param M: matrix
    :returns: tuple: indices of the min in M
    """
    idx = sp.nanargmin(M)
    j = int(idx % M.shape[1])
    i = int(sp.floor(idx / M.shape[1]))
    return i, j


def sortrows(data):
    """sort matrix by rows

    :type data: ndarray
    :param data: the ndarray that should be sorted by its rows
    :returns: ndarray : data sorted by its rows.
    """

    return sp.sort(
        data.view([('', data.dtype)] * data.shape[1]),
        axis=0
    ).view(data.dtype)

##---MAIN

if __name__ == '__main__':
    pass
