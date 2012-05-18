# -*- coding: utf-8 -*-
#
# spikeval - module.mod_metric_alignment.py
#
# Felix Franke <felfranke@googlemail.com>
# sometime in 2010
#
# adjusted for spikeval by Philipp Meier, Oct. 2011
#

"""spike train alignment metric"""
__docformat__ = 'restructuredtext'
__all__ = ['ModMetricAlignment']

##--- IMPORTS

import scipy as sp
from .base_module import BaseModule, ModuleInputError, ModuleExecutionError
from .result_types import MRTable, MRDict
from ..util import dict_arrsort, dict_list2arr, matrix_argmax

##---CLASSES

class ModMetricAlignment(BaseModule):
    """module: metric for spike train alignment

    computes the evaluation of spike sorting

    self.sts_ev contains the sorted spike trains - given the
    real/ideal/ground truth spike trains in self.sts_gt

    Calculates the similarity matrix between all pairs of spike trains from
    the
    ground truth and the estimation. This is used to find the optimal
    assignment between the spike trains, if one is a ground truth and the
    other is an estimation.

    Assignment Matrix:
        A label is assigned to every estimated spike. The following table
        lists all possible labels, given the different configurations is the
        ground truth. We assume E1 was found TO correlate with G1 and E2 is
        corresponding to G2. A "1" indicates a spike w.r.t. shift and jitter.

        =====  === === ===== == == ===== ====== ===== =====
        G1      1        1       1   1                  1
        G2          1    1                 1
        G3                           1     1      1
        =====  === === ===== == == ===== ====== ===== =====
        E1      1   1    1    1            1      1     1
        E2               1                        1     1
        =====  === === ===== == == ===== ====== ===== =====
        label  TP  FPA TPOvp FP FN FNOvp FPAOvp FPOGT

        TP : true positive
            E1 spike is assigned to associated ground truth spike train.
        FPA
            E1 spike is assigned to non associated ground truth spike
            train.
        TPOvp : true positive and overlap
            E1 spike is assigned to associated ground truth spike train and
            this spike participates in an overlap with another ground truth
            spike train.
        FP : false positive
            E1 spike is not assigned to any ground truth spike.
        FN : false negative
            There is no E1 spike for a spike in the associated ground truth
            spike train.
        FNOvp : false negative and overlap
            There is no E1 spike for a spike in the associated ground truth
            spike train and this spike participates in an overlap with
            another ground truth spike train.
        FPAOvp
            E1 spike is assigned to a spike of a non associated ground truth
             spike train and this spike participates in an overlap.

    :Parameters:
        self.sts_gt : dict of ndarray
            dict containing 1d ndarrays/lists of integers, representing the
            single unit spike trains. This is the ground truth.
        self.sts_ev : dict of ndarray
            dict containing 1d ndarrays/lists of integers, representing the
            single unit spike trains. this is the estimation.
        maxshift : int
            Upper bound for the tested shift of spike trains towards each
            other
            Default=15
        maxjitter : int
            upper bound for the tested jitter tolerance
            Default=6
        maxoverlapdistance : int
            upper bound for the tested overlap distance
            Default=45
    """

    # module interface

    RESULT_TYPES = [
        MRTable, # res_table
        MRTable, # similarity_matrix
        MRTable, # shift_matrix
        MRTable, # sp.atleast_2d(delta_shift)
        MRDict, # alignment
        MRDict, # O
        MRTable, # spike_no_assignment_matrix
        MRDict, # EL
        MRDict, # GL
        MRTable, # sp.atleast_2d(TP)
        MRTable, # sp.atleast_2d(TPO)
        MRTable, # sp.atleast_2d(FPA)
        MRTable, # sp.atleast_2d(FPAO)
        MRTable, # sp.atleast_2d(FN)
        MRTable, # sp.atleast_2d(FNO)
        MRTable, # sp.atleast_2d(FP)
        MRTable, # sp.atleast_2d(u_k2f)
        MRTable, # sp.atleast_2d(u_f2k)
    ]

    def _check_sts_gt(self, sts_gt):
        if sts_gt is None:
            raise ModuleInputError('sts_gt: '
                                   'needs ground truth spike train set')
        dict_list2arr(sts_gt)
        dict_arrsort(sts_gt)
        return sts_gt

    def _check_sts_ev(self, sts_ev):
        if sts_ev is None:
            raise ModuleInputError('sts_ev: '
                                   'needs evaluation spike train set')
        dict_list2arr(sts_ev)
        dict_arrsort(sts_ev)
        return sts_ev

    def _check_parameters(self, parameters):
        return {
            'sampling_rate':parameters.get('sampling_rate', 32000.0),
            'name':parameters.get('name', 'noname'),
            'maxshift':parameters.get('maxshift', 15),
            'maxjitter':parameters.get('maxjitter', 6),
            'maxoverlapdistance':parameters.get('maxoverlapdistance', 45), }

    def _apply(self):
        # inits and checks
        n = len(self.sts_gt)
        m = len(self.sts_ev)
        max_shift = self.parameters['maxshift']
        max_jitter = self.parameters['maxjitter']
        max_oldist = self.parameters['maxoverlapdistance']
        similarity_matrix = sp.zeros((n, m))
        shift_matrix = sp.zeros((n, m))
        sfuncs = sp.zeros((n, m, 2 * max_shift + 1))

        # compute similarity score and optimal shift between all pairs of
        # spike trains
        for i in xrange(n):
            for j in xrange(m):
                sfunc = ModMetricAlignment.similarity(
                    self.sts_gt[self.sts_gt.keys()[i]],
                    self.sts_ev[self.sts_ev.keys()[j]],
                    max_shift)
                similarity_matrix[i, j] = sfunc.max()
                shift_matrix[i, j] = sfunc.argmax() - max_shift
                sfuncs[i, j, :] = sfunc

        # shift all estimated spike trains so that they fit optimal to the
        # best matching true spike train
        u_f2k = sp.zeros(m)
        delta_shift = sp.zeros(m)
        for j in xrange(m):
            myidx = similarity_matrix[:, j].argmax()
            delta_shift[j] = shift_matrix[myidx, j]
            self.sts_ev[self.sts_ev.keys()[j]] =\
            self.sts_ev[self.sts_ev.keys()[j]] + delta_shift[j]

        # sort the spike train pairings according to their similarity measure
        # this ensures that the best matching spike trains will get all the
        # matching spikes. no spike that matches will thus be aligned to
        # another spike train.
        sorted_tupels = []
        S = similarity_matrix.copy()
        for i in xrange(n * m):
            maxidx = S.argmax()
            sorted_tupels.append((int(sp.floor(maxidx / m)), maxidx % m))
            S[sorted_tupels[i]] = -1

        # init alignment dictonary
        alignment = {}
        idx = 0
        for i in xrange(n):
            for j in xrange(m):
                alignment[(self.sts_gt.keys()[i], self.sts_ev.keys()[j])] = []
                idx += 1

        # convert self.sts_gt and self.sts_ev to lists, otherwise we cannot
        # remove objects
        GBlocked = {}
        EBlocked = {}
        num_known = sp.zeros(n)
        for i in xrange(n):
            num_known[i] = self.sts_gt[self.sts_gt.keys()[i]].shape[0]
            GBlocked[self.sts_gt.keys()[i]] = sp.zeros(
                self.sts_gt[self.sts_gt.keys()[i]].shape)
        num_found = sp.zeros(m)
        for j in xrange(m):
            num_found[j] = self.sts_ev[self.sts_ev.keys()[j]].shape[0]
            EBlocked[self.sts_ev.keys()[j]] = sp.zeros(
                self.sts_ev[self.sts_ev.keys()[j]].shape)

        # GBlocked will contain for every _inserted_ spike a 0 or a 1
        # 0: not assigned to any of the found spike trains => FN
        # 1: assigned to a spike of self.sts_ev => either TP or FN + FPA
        #
        # EBlocked will contain for every _found_ spike a 0 or a 1
        # 0: not assigned to any of the inserted spike trains => FP
        # 1: assigned to a spike of self.sts_gt => it will be handled when
        #    self.sts_gt is analyzed!

        spike_no_assignment_matrix = sp.zeros((n, m))
        # run over the sorted tuple and block all established spike assignments
        for i in xrange(n * m):
            k1idx = sorted_tupels[i][0]
            k2idx = sorted_tupels[i][1]
            k1 = self.sts_gt.keys()[sorted_tupels[i][0]]
            k2 = self.sts_ev.keys()[sorted_tupels[i][1]]
            train1 = self.sts_gt[k1]
            train2 = self.sts_ev[k2]
            idx1 = 0
            idx2 = 0
            while idx1 < len(train1) and idx2 < len(train2):
                # if a spike is blocked it cannot be associated anymore. jump
                if GBlocked[k1][idx1] == 1:
                    idx1 += 1
                    continue
                if EBlocked[k2][idx2] == 1:
                    idx2 += 1
                    continue

                if train2[idx2] + max_jitter >=\
                   train1[idx1] >=\
                   train2[idx2] - max_jitter:
                    # spike assignment found, remove spikes
                    alignment[(k1, k2)].append((idx1, idx2))
                    GBlocked[k1][idx1] = 1
                    EBlocked[k2][idx2] = 1

                    spike_no_assignment_matrix[k1idx, k2idx] += 1
                    # We cannot calculate TP/FP/FNs here, since we do not know
                    # yet which self.sts_gt belongs to which self.sts_ev (see
                    # next step)
                if train1[idx1] < train2[idx2]:
                    idx1 += 1
                else:
                    idx2 += 1

        # now establish the one to one relationships between the true and
        # found spike trains. this is a different relationship than the one
        # before because there can maximal be min(n,m) associations. If there
        # are more found spike trains than inserted (m>n), some wont have a
        # partner and be thus treated as FPs. If there are more inserted than
        # found (m>n) than some will be treated as being not found (FNs).

        # Assignment vectors between true and estimated units
        u_k2f = sp.ones(n, dtype=sp.int16) * -1
        u_f2k = sp.ones(m, dtype=sp.int16) * -1

        nAssociations = min(n, m)
        found = 0
        count = 0
        blocked_rows = []
        blocked_cols = []
        snam = spike_no_assignment_matrix.copy()
        while (found < nAssociations) and (count < n * m):
            i, j = matrix_argmax(snam)
            if i not in blocked_rows and j not in blocked_cols:
                blocked_rows.append(i)
                u_k2f[i] = j
                blocked_cols.append(j)
                u_f2k[j] = i
                found += 1
            snam[i, j] = -1
            count += 1

        # now we want to calculate FPs and FNs. Since in
        # spike_no_assignment_matrix the assigned spikes are coded and in
        # u_k2f and u_f2k the assignments of the units to each other, we can
        # now compare the number of assignments to the total number of spikes
        # in the corresponding trains. this will directly give the
        # correct/error numbers.

        # mark all the overlapping spikes
        ret = ModMetricAlignment.overlaps(self.sts_gt, max_oldist)
        O = ret['O']
        NO = ret['Onums']

        # initialize dictionaries for labels for all spikes
        GL = {}
        for k in self.sts_gt.keys():
            GL[k] = sp.zeros(self.sts_gt[k].shape, dtype=sp.int16)
        EL = {}
        for k in self.sts_ev.keys():
            EL[k] = sp.zeros(self.sts_ev[k].shape, dtype=sp.int16)


        # run over every single spike and check which label it gets
        #             1      2      3     4       5     6      7
        labelList = ['TP', 'TPO', 'FP', 'FPA', 'FPAO', 'FN', 'FNO']
        TP = sp.zeros(n)
        TPO = sp.zeros(n)
        FP = sp.zeros(m) # m !!
        FPA = sp.zeros(n)
        FPAO = sp.zeros(n)
        FPA_E = sp.zeros(m) # m!!
        FPAO_E = sp.zeros(m) # m!!
        FN = sp.zeros(n)
        FNO = sp.zeros(n)
        # handle the spikes which were aligned first
        for i in xrange(n):
            k1 = self.sts_gt.keys()[i]
            for j in xrange(m):
                k2 = self.sts_ev.keys()[j]
                for a in xrange(len(alignment[(k1, k2)])):
                    ovp = O[k1][alignment[(k1, k2)][a][0]]
                    # labels = ['TP', 'TPO', 'FP', 'FPA', 'FPAO', 'FN', 'FNO']
                    if u_k2f[i] == j:
                        if ovp == 1:
                            GL[k1][alignment[(k1, k2)][a][0]] = 2 # TPO
                            EL[k2][alignment[(k1, k2)][a][1]] = 2
                            TPO[i] += 1
                        else:
                            GL[k1][alignment[(k1, k2)][a][0]] = 1 # TP
                            EL[k2][alignment[(k1, k2)][a][1]] = 1
                            TP[i] += 1
                    else:
                        if ovp == 1:
                            GL[k1][alignment[(k1, k2)][a][0]] = 5 #FPAO
                            EL[k2][alignment[(k1, k2)][a][1]] = 5
                            FPAO[i] += 1
                            FPAO_E[j] += 1
                            # Count assignment errors twice! FP + FN
                        else:
                            GL[k1][alignment[(k1, k2)][a][0]] = 4 # FPA
                            EL[k2][alignment[(k1, k2)][a][1]] = 4
                            FPA[i] += 1
                            FPA_E[j] += 1
                            # Count assignment errors twice!

            # Now check all spikes of i which have no labels. those are FNs
            for spk in xrange(len(GL[k1])):
                if GL[k1][spk] == 0:
                    if O[k1][spk] == 1:
                        GL[k1][spk] = 7  # FNO
                        FNO[i] += 1
                    else:
                        GL[k1][spk] = 6  # FN
                        FN[i] += 1
                        # The last thing to do is to check all labels of
                        # spikes in self.sts_ev. Those which have no label
                        # yet are FPs
        for j in xrange(m):
            k2 = self.sts_ev.keys()[j]
            FP[j] = 0
            for spk in xrange(len(EL[k2])):
                if EL[k2][spk] == 0:
                    EL[k2][spk] = 3 # FP
                    FP[j] += 1

        res_table_headers = [
            'GT Unit ID', # ID of gt unit
            'Found Unit ID', # ID of associated ev unit
            'Known Spikes', # nos of gt unit
            'Overlapping Spikes', # nos of overlaps
            'Found Spikes', # nos of associated ev unit
            'True Pos', # nos which are assigned to the associated gt unit.
            'True Pos Ovps', # nos of overlaps
            'False Pos Assign GT', # nos of ev unit which are assigned to
            # to a non-associated gt unit
            'False Pos Assign Found', #
            'False Pos Ovps GT', # FPAO
            'FPs Assign Ovps Found', # FPAO_E
            'False Neg', #
            'False Neg Overlaps', #
            'False Pos', #
        ]
        res_table = []

        # build a table with one row for every assignment of two spike trains
        # and one row for every unassigned spike train.
        # Problem: The number of false positive assignments for one of the
        # assignment rows has to be the sum of the individual assignment
        # errors ???? ->This way an assignment error counts as 2 errors
        # (one FP and one FN).

        remaining_found_units = sp.ones(m)
        # build the assignment rows and unassigned ground truth spike train
        # rows first
        for i in xrange(n):
            unitk = self.sts_gt.keys()[i]
            known = num_known[i]
            overlapping = NO[i]
            tp = TP[i]
            tpo = TPO[i]
            fn = FN[i]
            fno = FNO[i]
            fpa = FPA[i]
            fpao = FPAO[i]

            j = u_k2f[i]
            unitf = ''
            found = fp = fpae = fpaoe = 0
            if j >= 0:
                remaining_found_units[j] = 0
                unitf = self.sts_ev.keys()[j]
                found = num_found[j]
                fp = FP[j]
                fpae = FPA_E[j]
                fpaoe = FPAO_E[j]

            res_table.append([unitk, unitf, known, overlapping, found, tp,
                              tpo, fpa, fpae, fpao, fpaoe, fn, fno, fp])

        # Append "False Positive Unit" which has all found spikes of found
        # units which were not assigned to a ground truth unit
        for j in xrange(m):
            if remaining_found_units[j] == 1:
                unitk = ''
                known = overlapping = tp = tpo = fn = fno = fpa = fpao = 0
                unitf = self.sts_ev.keys()[j]
                found = num_found[j]
                fp = FP[j]
                fpae = FPA_E[j]
                fpaoe = FPAO_E[j]
                res_table.append([unitk, unitf, known, overlapping, found, tp,
                                  tpo, fpa, fpae, fpao, fpaoe, fn, fno, fp])

        # Build return _value dictionary
        self.result = [
            MRTable(res_table, header=res_table_headers), # table
            similarity_matrix, # table
            shift_matrix, # table
            sp.atleast_2d(delta_shift), # table
            alignment, # dict
            O, #dict
            spike_no_assignment_matrix, # table
            EL, # dict
            GL, # dict
            sp.atleast_2d(TP), # table
            sp.atleast_2d(TPO), # table
            sp.atleast_2d(FPA), # table
            sp.atleast_2d(FPAO), # table
            sp.atleast_2d(FN), # table
            sp.atleast_2d(FNO), # table
            sp.atleast_2d(FP), # table
            sp.atleast_2d(u_k2f), # table
            sp.atleast_2d(u_f2k), # table
        ]

    @staticmethod
    def similarity(st1, st2, mtau):
        """calculates xcorr function between spike trains st1 and st2"""

        rval = sp.zeros(2 * mtau + 1)
        for tau in xrange(-mtau, mtau + 1):
            rval[tau + mtau] = ModMetricAlignment.simi_kernel(st1, st2 + tau)
        return rval

    @staticmethod
    def simi_kernel(s1, s2):
        """Calculates the normalized scalar product between two binary vectors
        which are given by two point processes without actually creating the
        binary vectors.
        """

        p = 0
        s1idx = 0
        s2idx = 0
        while s1idx < s1.shape[0] and s2idx < s2.shape[0]:
            if s1[s1idx] == s2[s2idx]:
                p += 1

            if s1[s1idx] < s2[s2idx]:
                s1idx += 1
            else:
                s2idx += 1

        return 2.0 * p / (s1.shape[0] + s2.shape[0])

    @staticmethod
    def overlaps(sts, window):
        """Calculates a "boolean" dictonary, indicating for every spike in
        every spiketrain in sts whether it belongs to an overlap or not"""
        n = len(sts)
        O = {}
        for k in sts.keys():
            O[k] = sp.zeros(sts[k].shape, dtype=sp.bool_)
        Onums = sp.zeros(len(sts))
        # run over all pairs of spike trains in G
        for i in xrange(n):
            for j in xrange(i + 1, n):
                # for every pair run over all spikes in i and check whether a
                # spike in j overlaps
                trainI = sts[sts.keys()[i]]
                trainJ = sts[sts.keys()[j]]
                idxI = 0
                idxJ = 0
                while idxI < len(trainI) and idxJ < len(trainJ):
                    # Overlapping?
                    if abs(trainI[idxI] - trainJ[idxJ]) < window:
                        # Every spike can only be in one or no overlap.
                        # prevents triple counting
                        if O[sts.keys()[i]][idxI] == 0:
                            O[sts.keys()[i]][idxI] = 1
                            Onums[i] += 1
                        if O[sts.keys()[j]][idxJ] == 0:
                            O[sts.keys()[j]][idxJ] = 1
                            Onums[j] += 1

                    if trainI[idxI] < trainJ[idxJ]:
                        idxI += 1
                    else:
                        idxJ += 1
        ret = {'O':O, 'Onums':Onums}
        return ret

##--- MAIN

if __name__ == '__main__':
    pass
