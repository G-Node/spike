#﻿# -*- coding: utf-8 -*-
################################################################################
##
##  Copyright 2010 Philipp Meier <pmeier82@googlemail.com>
##
##  Licensed under the EUPL, Version 1.1 or – as soon they will be approved by
##  the European Commission - subsequent versions of the EUPL (the "Licence");
##  You may not use this work except in compliance with the Licence.
##  You may obtain a copy of the Licence at:
##
##  http://ec.europa.eu/idabc/eupl
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the Licence is distributed on an "AS IS" basis,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the Licence for the specific language governing permissions and
##  limitations under the Licence.
##
################################################################################
#
# nsim - cluster_dynamics.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-04-12
#
# watered down version for spike_evaluation website
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2012-04-16
#

"""point processes w/ and w/o correlations to generate spiketrains"""
__doctype__ = 'restructuredtext'

##---IMPORTS

# packages
import scipy as sp

##---FUNCTIONS

def cluster_process(single_rates, nsmpls, srate, o2rate=5.0, o3rate=1.0):
    """produce spike trains for `n` units with overlap rates.

    :type single_rates: ndarray
    :param single_rates: List of firing rates (in Hz) for the single units
        in the cluster
    :type nsmpls: int
    :param nsmpls: Length of the simulated events in samples.
    :type srate: float
    :param srate: Sample rate (in Hz).
    :type o2rate: float
    :param o2rate: Overlap of 2 events, rate in Hertz. If 0.0 do not put
        overlaps.
        Default=5.0
    :type o3rate: float
    :param o3rate: Overlap of 3 events, rate in Hertz. If 0.0 do not put
        overlaps.
        Default=1.0
    """

    # inits
    if not isinstance(single_rates, sp.ndarray):
        single_rates = sp.asarray(single_rates)
    srate = float(srate)
    cumrate = float(single_rates.sum())
    events = sp.asarray(poi_pproc_refper(cumrate, srate, nsmpls))
    props = single_rates / cumrate
    rval = [[] for i in xrange(single_rates.size)]
    o2mem = [[] for i in xrange(single_rates.size)]
    o3mem = [[] for i in xrange(single_rates.size)]

    # label single events according rate statistics
    for e in events:
        rval[label_event(props)].append(e)

    # TODO: assert overlaps of order n do not accidentally produce overlaps of
    # order n+1 or higher

    # overlaps of 2 units
    if o2rate > 0.0 and single_rates.size > 1 and events.size > cumrate /\
                                                                o2rate:
        for i in xrange(int(o2rate * nsmpls / srate)):
            # find unit1 and unit2
            u1 = u2 = label_event(props)
            while u1 == u2:
                u2 = label_event(props)

            # generate random event in range and find unit events closest
            my_ev = int(sp.rand() * nsmpls)
            u1_ev, _ = find_close(my_ev, rval[u1])
            u2_ev, _ = find_close(my_ev, rval[u2])
            my_ev = jitter_overlaps(my_ev, int(srate / 1000.0), 2)

            # save info and replace events with new overlap event
            rval[u1].insert(u1_ev, my_ev[0])
            rval[u1].pop(u1_ev + 1)
            o2mem[u1].append(my_ev[0])
            rval[u2].insert(u2_ev, my_ev[1])
            rval[u2].pop(u2_ev + 1)
            o2mem[u2].append(my_ev[1])

            # TODO: any break criteria?

    # overlaps of 3 units
    if o3rate > 0.0 and single_rates.size > 2 and events.size > cumrate /\
                                                                o3rate:
        for i in xrange(int(o3rate * nsmpls / srate)):
            # find unit1, unit2 and unit3
            u1 = u2 = u3 = label_event(props)
            while u2 == u1:
                u2 = label_event(props)
            while u3 == u1 or u3 == u2:
                u3 = label_event(props)

            # generate random event in range and find unit events closest
            my_ev = int(sp.rand() * nsmpls)
            u1_ev, _ = find_close(my_ev, rval[u1])
            u2_ev, _ = find_close(my_ev, rval[u2])
            u3_ev, _ = find_close(my_ev, rval[u3])
            my_ev = jitter_overlaps(my_ev, int(srate / 1000.0), 3)

            # save info and replace events with new overlap event
            rval[u1].insert(u1_ev, my_ev[0])
            rval[u1].pop(u1_ev + 1)
            o3mem[u1].append(my_ev[0])
            rval[u2].insert(u2_ev, my_ev[1])
            rval[u2].pop(u2_ev + 1)
            o3mem[u2].append(my_ev[1])
            rval[u3].insert(u3_ev, my_ev[2])
            rval[u3].pop(u3_ev + 1)
            o3mem[u3].append(my_ev[2])

            # TODO: any break criteria?

    # return
    return rval, o2mem, o3mem


def label_event(props):
    """label an event according to a discrete probability distribution

    :type props: ndarray
    :param props: The probabilities of the discrete distribution to draw from.
    :returns: The label as the index into the props array or -1 on error.
    """

    # inits
    if props.sum() != 1.0:
        raise ValueError('props is not normalized')

    # labeling
    rnd = sp.rand()
    for i in xrange(props.size):
        if rnd <= props.cumsum()[i]:
            return i
    return - 1


def find_close(x, y_vec):
    """finds the index and difference of the closest element in y_vec to x

    :type x: float
    :param x: the matching item
    :type y_vec: ndarray
    :param y_vec: the array to look up
    """

    # inits
    rval = -1, None

    # search
    for i in xrange(len(y_vec)):
        temp = sp.absolute(y_vec[i] - x)
        if rval[1] is None or temp < rval[1]:
            rval = i, temp

    # return
    return rval


def jitter_overlaps(x, tol, n, nstd=4.0):
    """jitter events so they are within at most tol samples of each other

    :type x: int
    :param x: offset
    :type tol: int
    :param tol: max jitter range
    :type n: int
    :param n: n points to generate
    :type nstd: float
    :param nstd: how many unit std of spread are allowed
    """

    return (sp.randn(n) * tol / float(nstd) + x).astype(int)


def poi_pproc_refper(frate, srate, nsmpls, refper=2.5):
    """generate events from a poisson distribution w.r.t refractory period

    :type frate: float
    :param frate: expected firing rate in Hz
    :type srate: float
    :param srate: sample rate in Hz
    :type nsmpls: int
    :param nsmpls: generate spike train for that many samples
    :type refper: int
    :param refper: refractory period in ms
        Default=2.5
    :rtype: list
    :returns: spiketrain
    """

    # refractory period
    refper = int(refper * srate / 1000.0)
    if refper * frate > srate:
        raise ValueError('inconsistent values for frate, srate and refper!')

    # inits
    rval = []
    lam = float(srate - frate * refper) / float(frate)
    interval_kernel = lambda:-lam * sp.log(sp.rand())

    # produce train
    event_current = 0
    while event_current < nsmpls:
        # draw interval sample
        interv = int(interval_kernel())
        if interv < refper:
            continue
            # its ok
        event_current += interv
        rval.append(event_current)

    if len(rval) > 0:
        if rval[-1] >= nsmpls:
            rval.pop(-1)

    # return
    return rval

##---MAIN

if __name__ == '__main__':
    pass
