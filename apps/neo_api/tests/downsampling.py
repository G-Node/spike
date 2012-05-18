# testing different ways to downsample the time series (Analog Signal), using 
# numpy / scipy

import numpy as np
from scipy import signal 
import timeit
import sys

as_10x4 = np.random.rand(10 ** 4)
as_10x5 = np.random.rand(10 ** 5)
as_10x6 = np.random.rand(10 ** 6)

lengths  = (10 ** 4, 10 ** 5, 10 ** 6)
scales = (5000, 1000)
 
# using downsample
def sci_down(a, s):
    return signal.decimate(a, int(round(len(a)/s)))
 
# using resample
def sci_resa(a, s):
    return signal.resample(a, s)

if __name__ == "__main__":
    for l in lengths:
        print "Testing with %d-length array:" % l
        for s in scales:
            a = np.random.rand(l)
            print "Scale %d" % s
            t = timeit.Timer('sci_down(a, %d)' % s, 'from __main__ import sci_down, a')
            elapsed = (1000 * t.timeit(number=10)/10) # result should be in ms
            print "Using DOWNsampling takes %0.3f milliseconds/pass" % elapsed
            t = timeit.Timer('sci_resa(a, %d)' % s, 'from __main__ import sci_resa, a')
            elapsed = (1000 * t.timeit(number=10)/10) # result should be in ms
            print "Using REsampling takes %0.3f milliseconds/pass" % elapsed
