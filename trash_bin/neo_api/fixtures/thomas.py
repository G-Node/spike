# add performance testing!!

import sys
sys.path.append("/data/apps/g-node-portal/neoapi/")
import django_access
import unittest
import datetime as dte
import math
import numpy as np
from neo_api.models import *
from django.contrib.auth.models import User


meta_channels = [1, 2, 4, 5, 6, 9, 10, 11, 12, 13, 14, 16]

def convert_to_timeseries(line):
    """
    Converts a string of floats into a list. 
    """
    s = line.split(" ")
    for i in range(s.count('')):
        s.remove('')
    return s


def create_thomas():
    """
    This function creates NEO objects using Django ORM. It requires initial data
    in files, located 
    ./080707/lfp_fix080707.dat
    ./080707/lfp_sac080707.dat
    Normally, one can find these files at 
    gate.g-node.org:/groups/g-node-core/data/spike_lfp/
    """
    u = User.objects.get(pk=12) # Change user!
    s_offset = len(Segment.objects.all()) # set the correct segment ID offset up!
    r_offset = len(RecordingChannel.objects.all()) # set the correct recording channel ID offset up!
    b = Block()
    b.name = "Macaque Monkey Recordings, LFPs, V1"
    b.filedatetime = dte.datetime.now()
    b.index = 1
    b.author = u
    b.date_created = dte.datetime.now()
    b.save()
    # processing LFP FIX
    flag = math.floor(176*12/10)
    f = open('080707/lfp_fix080707.dat', 'r')
    for i, l in enumerate(f):
        if i < 176:
            s = new_segment(i, b, u) # create new segment
            for e in range(5): # create 5 random events - for WDAT testing
                e = new_event(e, s, u)
        else:
            s = Segment.objects.get(id=int(math.fmod(i, 176)) + s_offset)
        if float(i)/176 == math.floor(float(i)/176):
            # create new recording channel
            r = RecordingChannel()
            r.name = "Channel %d" % meta_channels[int(math.floor(float(i)/176))]
            r.index = meta_channels[int(math.floor(float(i)/176))]
            r.author = u
            r.date_created = dte.datetime.now()
            r.save()
        # creating analogsignal
        ts = convert_to_timeseries(l)
        a = new_signal(i, "FIX", s, r, ts, u)
        # every 10% of file processed
        if float(i)/flag == math.floor(float(i)/flag):
            print "%s percent of LFP FIX processed." % int(math.floor(float(i)/flag) * 10)
    f.close()
    # processing LFP SAC
    flag = math.floor(368*12/10)
    f = open('080707/lfp_sac080707.dat', 'r')
    for i, l in enumerate(f):
        if i < 368:
            # create new segment
            s = new_segment(i, b, u)
            for e in range(5): # create 5 random events - for WDAT testing
                e = new_event(e, s, u)
        else:
            s = Segment.objects.get(id=int(math.fmod(i, 176)) + 175 + s_offset)
        if float(i)/368 == math.floor(float(i)/368):
            # get the recording channel
            r = RecordingChannel.objects.get(id=math.floor(float(i)/368) + r_offset)
        ts = convert_to_timeseries(l)
        a = new_signal(i, "SAC", s, r, ts, u)
        # every 10% of file processed
        if float(i)/flag == math.floor(float(i)/flag):
            print "%s percent of LFP SAC processed." % int(math.floor(float(i)/flag) * 10)
    f.close()
    print "Data imported successfully. Bye."

def new_segment(i, b, u):
    s = Segment()
    s.name = "Trial %d" % i
    s.filedatetime = dte.datetime.now()
    s.index = i
    s.block = b
    s.author = u
    s.date_created = dte.datetime.now()
    s.save()
    return s

def new_event(i, s, u):
    e = Event()
    e.label = "This is a random label #%d" % i
    e.time = np.random.random()
    e.time__unit = "ms"
    e.segment = s
    e.author = u
    e.date_created = dte.datetime.now()
    e.save()
    return e

def new_signal(i, typ, s, r, ts, u):
    a = AnalogSignal()
    a.name = "LFP %s Signal-%d" % (typ, i)
    a.t_start = 0.0
    a.t_start__unit = "ms"
    a.sampling_rate = 20000 # ???
    a.sampling_rate__unit = "hz"
    a.segment = s
    a.recordingchannel = r
    a.signal_data = ", ".join([str(value) for value in ts])
    a.signal__unit = "mv"
    a.signal_size = len(ts) * 4
    a.author = u
    a.date_created = dte.datetime.now()
    a.save()
    return a

if __name__ == '__main__':
    create_thomas()



