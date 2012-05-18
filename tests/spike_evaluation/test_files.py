##--IMPORTS

from tables import openFile
import scipy as sp

from cluster_dynamics import cluster_process


##---FUNCTIONS

def waveform_prototype(samples=40):
    """creates a single channel waveform prototype

    :type samples: int
    :param samples: length of the waveform in samples
    """

    wf = sp.sin(sp.linspace(-0.5 * sp.pi, 2.5 * sp.pi, samples))
    wf *= sp.linspace(0, 2, samples)
    wf *= sp.hanning(samples)
    return wf


def generate_single_unit(wf, spike_train, end):
    """generate a single unit spike train * waveform convolution

    :type wf: ndarray
    :param wf: multi-channeled waveform of the unit
    :type spike_train: ndarray
    :param spike_train: spike train of this unit
    :type end: int
    :param end: end time of the data strip in samples
    """

    tf, nc = wf.shape
    spike_train = spike_train[spike_train < end]
    rval = sp.zeros((end, nc))
    for t in spike_train:
        rval[t:t + tf, :] += wf
    return rval


def generate_multi_unit(tf, nc, end, ampl, rates, srate=1000.0, o2rate=10.0,
                        o3rate=0.0):
    """generate a multiunit spike train * waveform convolution

    :type tf: int
    :param tf: waveform length in samples
    :type nc: int
    :param nc: number of channels
    :type end: int
    :param end: end time of the data strip in samples
    :type ampl: dict
    :param ampl: dict of amplitude distributions for each unit
    :type rates: dict
    :param rates: dict of fire rates for each unit in Hz
    :type srate: float
    :param srate: sampling rate in Hz
        Default = 1000.0
    :type o2rate: float
    :param o2rate: rate of doublet overlaps in Hz
        Default=10.0
    :type o3rate: float
    :param o3rate: rate of triplet overlaps in Hz
        Default=0.0
    """

    # inits and checks
    assert isinstance(ampl, dict), 'ampl is not a dict'
    assert len(ampl) > 0, 'no entries in ampl'
    nunits = len(ampl)
    assert ampl.keys() == rates.keys(), 'ampl and rates must have same key set'
    key_list = sorted(ampl.keys())
    rval = dict(zip(key_list, [sp.zeros((end, nc))
                               for _ in xrange(nunits)]))

    # build waveforms
    wf = waveform_prototype(tf)
    wfs = dict(zip(key_list, [sp.zeros((tf, nc))
                              for _ in xrange(nunits)]))
    for k in key_list:
        for c in xrange(nc):
            wfs[k][:, c] = wf * ampl[k][c]

    # build spike trains
    single_rates = [rates[k] for k in key_list]
    sts_raw, o2, o3 = cluster_process(single_rates, end - tf, srate, o2rate,
                                      o3rate)
    sts = dict(zip(key_list, map(sp.asarray, sts_raw)))

    # build instrinsic spike trains
    ists = dict(zip(key_list, [generate_single_unit(wfs[k], sts[k], end)
                               for k in key_list]))

    # build intrinsic data strip
    data = sp.zeros((end, nc))
    for k in key_list:
        data += ists[k]

    # return
    return data, sts, srate


def archives_from_data_and_sts(path, name, data, sts, srate):
    """create archives for testing

    :type path: str
    :param path: save path
    :type name: str
    :param name: file name prefix
    :type data: ndarray
    :param data: raw data for h5 file
    :type sts: dict (spike train set)
    :param sts: spike train set, one spike train per unit
    """

    # imports
    from os.path import join, exists, isdir
    from spikeval.datafiles import create_hdf5_arc, create_gdf

    # inits and checks
    assert exists(path), 'invalid path: %s' % path
    assert isdir(path), 'path is no directory: %s' % path
    rd_name = join(path, ''.join([name, '-rd.h5']))
    gt_name = join(path, ''.join([name, '-gt.gdf']))

    # save
    create_hdf5_arc(rd_name, data, srate)
    create_gdf(gt_name, sts)


def corrupt_ground_truth(gt_name, tp, fp, fn, fpa):
    """corrupts the gt file to generate a more interesting result
    """
    pass

if __name__ == '__main__':
    data, sts, srate = generate_multi_unit(
        20, 2, 10000, {0:[1.0, 5.0], 1:[5.0, 1.0]}, {0:10.0, 1:10.0})

    noise10 = sp.randn(*data.shape) * 1.0
    noise15 = sp.randn(*data.shape) * 1.5
    noise20 = sp.randn(*data.shape) * 2.0

    archives_from_data_and_sts('/home/phil/Data/test',
                               'bmark-test-10',
                               data + noise10,
                               sts,
                               srate)
    archives_from_data_and_sts('/home/phil/Data/test',
                               'bmark-test-15',
                               data + noise15,
                               sts,
                               srate)
    archives_from_data_and_sts('/home/phil/Data/test',
                               'bmark-test-20',
                               data + noise20,
                               sts,
                               srate)
