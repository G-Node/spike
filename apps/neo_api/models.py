from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.core.exceptions import PermissionDenied, ValidationError

import numpy as np
from scipy import signal
from fields import models as fmodels
from datafiles.models import Datafile
from meta import meta_unit_types, meta_objects, meta_messages, meta_children, factor_options

# default unit values and values limits
name_max_length = 100
label_max_length = 100
unit_max_length = 10

def_time_unit = "ms"
def_data_unit = "mV"
def_samp_unit = "Hz"

# supporting functions
#===============================================================================

def _find_nearest(array, value):
    """
    Finds index of the nearest value to the given value in the given array.
    """
    idx = (np.abs(array - float(value))).argmin()
    return idx

def _data_as_list(data):
    """
    Returns a list of floats from comma-separated text or empty list.
    """
    l = []
    if len(data):
        for s in str(data).split(','):
            l.append(float(s))
    return l

def _clean_csv(arr):
    """
    Parses a given list and returns a string of comma-separated float values.
    """
    if not type(arr) == type([]):
        raise ValueError("data provided is not a list.")
    cleaned_data = ""
    for value in arr:
        try:
            a = float(value)
            cleaned_data += ', ' + str(a)
        except:
            raise ValueError(str(value))
    if len(cleaned_data) > 0:
        cleaned_data = cleaned_data[2:]
    return cleaned_data


class BaseInfo(models.Model):
    """
    Basic info about any NEO object created at G-Node.

    State:
    Active <--> Deleted -> Archived

    """
    STATES = (
        (10, 'Active'),
        (20, 'Deleted'),
        (30, 'Archived'),
    )
    _current_state = models.IntegerField('current state', choices=STATES, default=10)
    author = models.ForeignKey(User)
    date_created = models.DateTimeField('date created', default=datetime.now,\
        editable=False)
    file_origin = models.ForeignKey(Datafile, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True) # Resp. H: Last-modified

    # this is temporary unless the integration with Datafiles is implemented
    def is_accessible(self, user):
        return self.author == user

    def can_edit(self, user):
        return self.author == user

    def is_sliceable(self): return False

    class Meta:
        abstract = True

    @property
    def obj_type(self):
        """
        Returns the type of the object (string), like 'segment' or 'event'.
        """
        for obj_type in meta_objects:
            if isinstance(self, meta_classnames[obj_type]):
                return obj_type
        raise TypeError("Critical error. Panic. NEO object can't define it's own type. Tell system developers.")

    @property
    def neo_id(self):
        """ Returns NEO_ID. Example of neo_id: 'segment_1435' """
        return "%s_%d" % (self.obj_type, self.id)

    @property
    def info(self):
        raise NotImplementedError("This is an abstract class")

    @property
    def size(self):
        """
        used as default for Events, Epochs etc. which have a fixed small
        non-significant size
        """
        return 0 

    @property
    def current_state(self):
        """ active <-> deleted -> archived """
        return self._current_state

    def is_active(self):
        return self.current_state == 10

    def delete(self):
        self._current_state = 20

    def archive(self):
        self._current_state = 30

    def restore(self):
        self._current_state = 10


# basic NEO classes
#===============================================================================

# 1 (of 15)
class Block(BaseInfo):
    """
    NEO Block @ G-Node.
    """
    # NEO attributes
    name = models.CharField('name', max_length=name_max_length)
    filedatetime = models.DateTimeField('filedatetime', null=True, blank=True)
    index = models.IntegerField('index', null=True, blank=True)

    @property
    def info(self):
        pass

    @property
    def size(self):
        return int(np.array([w.size for w in self.segment_set.all()]).sum())


# 2 (of 15)
class Segment(BaseInfo):
    """
    NEO Segment @ G-Node.
    """
    # NEO attributes
    name = models.CharField('name', max_length=name_max_length)
    filedatetime = models.DateTimeField('filedatetime', null=True, blank=True)
    index = models.IntegerField('index', null=True, blank=True)
    # NEO relationships
    block = models.ForeignKey(Block, blank=True, null=True)

    @property
    def size(self):
        return int(np.array([np.array([w.size for w in getattr(self, child + \
            "_set").all()]).sum() for child in meta_children["segment"]]).sum())


# 3 (of 15)
class EventArray(BaseInfo):
    """
    NEO EventArray @ G-Node.
    """
    # no NEO attributes
    # NEO relationships
    segment = models.ForeignKey(Segment, blank=True, null=True)

# 4 (of 15)
class Event(BaseInfo):
    """
    NEO Event @ G-Node.
    """
    # NEO attributes
    label = models.CharField('label', max_length=label_max_length)
    time = models.FloatField('time')
    time__unit = fmodels.TimeUnitField('time__unit', default=def_time_unit)
    # NEO relationships
    segment = models.ForeignKey(Segment, blank=True, null=True)
    eventarray = models.ForeignKey(EventArray, blank=True, null=True)

    @property
    def is_alone(self):
        """
        Indicates whether to show an object alone, even if it is organized in
        an EventArray.
        """
        return (self.eventarray.count() == 0)

# 5 (of 15)
class EpochArray(BaseInfo):
    """
    NEO EpochArray @ G-Node.
    """
    # no NEO attributes
    # NEO relationships
    segment = models.ForeignKey(Segment, blank=True, null=True)

# 6 (of 15)
class Epoch(BaseInfo):
    """
    NEO Epoch @ G-Node.
    """
    # NEO attributes
    label = models.CharField('label', max_length=label_max_length)
    time = models.FloatField('time')
    time__unit = fmodels.TimeUnitField('time__unit', default=def_time_unit)
    duration = models.FloatField('duration')
    duration__unit = fmodels.TimeUnitField('duration__unit', default=def_time_unit)
    # NEO relationships
    segment = models.ForeignKey(Segment, blank=True, null=True)
    epocharray = models.ForeignKey(EpochArray, blank=True, null=True)

    @property
    def is_alone(self):
        """
        Indicates whether to show an object alone, even if it is organized in
        an EpochArray.
        """
        return (self.epocharray.count() == 0)

# 7 (of 15)
class RecordingChannelGroup(BaseInfo):
    """
    NEO RecordingChannelGroup @ G-Node.
    """
    # NEO attributes
    name = models.CharField('name', max_length=name_max_length)
    # NEO relationships
    block = models.ForeignKey(Block, blank=True, null=True)


# 8 (of 15)
class RecordingChannel(BaseInfo):
    """
    NEO RecordingChannel @ G-Node.
    """
    # NEO attributes
    name = models.CharField('name', max_length=name_max_length)
    index = models.IntegerField('index', null=True, blank=True)
    # NEO relationships
    recordingchannelgroup = models.ForeignKey(RecordingChannelGroup, blank=True, null=True)


# 9 (of 15)
class Unit(BaseInfo):
    """
    NEO Unit @ G-Node.
    """
    # NEO attributes
    name = models.CharField('name', max_length=name_max_length)
    # NEO relationships
    recordingchannel = models.ManyToManyField(RecordingChannel, blank=True, null=True)


# 10 (of 15)
class SpikeTrain(BaseInfo):
    """
    NEO SpikeTrain @ G-Node.
    """
    # NEO attributes
    t_start = models.FloatField('t_start')
    t_start__unit = fmodels.TimeUnitField('t_start__unit', default=def_time_unit)
    t_stop = models.FloatField('t_stop', blank=True, null=True)
    t_stop__unit = fmodels.TimeUnitField('t_stop__unit', default=def_time_unit)
    # NEO relationships
    segment = models.ForeignKey(Segment, blank=True, null=True)
    unit = models.ForeignKey(Unit, blank=True, null=True)
    # NEO data arrays
    times_data = models.TextField('spike_data', blank=True) # use 'spike_times' property to get data
    times__unit = fmodels.TimeUnitField('spike_data__unit', default=def_data_unit)
    times_size = models.IntegerField('times_size', blank=True) # in bytes, for better performance

    @apply
    def times():
        def fget(self):
            return _data_as_list(self.times_data)
        def fset(self, arr):
            self.times_data = _clean_csv(arr)
        def fdel(self):
            pass
        return property(**locals())

    @property
    def size(self):
        return int(np.array([w.size for w in self.waveform_set.all()]).sum()) +\
            self.times_size

    def save(self, *args, **kwargs):
        # override save to keep signal size up to date
        self.times_size = len(self.times) * 24
        super(SpikeTrain, self).save(*args, **kwargs)


# 11 (of 15)
class AnalogSignalArray(BaseInfo):
    """
    NEO AnalogSignalArray @ G-Node.
    """
    # NEO relationships
    segment = models.ForeignKey(Segment, blank=True, null=True)
    recordingchannelgroup = models.ForeignKey(RecordingChannelGroup, blank=True, null=True)

    # NEO attributes
    @property
    def sampling_rate(self):
        pass

    @property
    def s_start(self):
        pass

    @property
    def size(self):
        return int(np.array([w.size for w in self.analogsignal_set.all()]).sum())


# 12 (of 15)
class AnalogSignal(BaseInfo):
    """
    NEO AnalogSignal @ G-Node.
    """
    # NEO attributes
    name = models.CharField('name', max_length=name_max_length)
    sampling_rate = models.FloatField('sampling_rate')
    sampling_rate__unit = fmodels.SamplingUnitField('sampling_rate__unit', default=def_samp_unit)
    t_start = models.FloatField('t_start')
    t_start__unit = fmodels.TimeUnitField('t_start__unit', default=def_time_unit)
    # NEO relationships
    segment = models.ForeignKey(Segment, blank=True, null=True)
    recordingchannel = models.ForeignKey(RecordingChannel, blank=True, null=True)
    analogsignalarray = models.ForeignKey(AnalogSignalArray, blank=True, null=True)
    # NEO data arrays
    signal_data = models.TextField('signal_data') # use 'signal' property to get data
    signal__unit = fmodels.SignalUnitField('signal__unit', default=def_data_unit)
    signal_size = models.IntegerField('signal_size', blank=True) # in bytes, for better performance

    def get_slice(self, start_time=None, end_time=None, start_index=None,\
            end_index=None, duration=None, samples_count=None, downsample=None):
        """
        Implements dataslicing/downsampling. Floats/integers are expected.
        'downsample' parameter defines the new resampled resolution.
        """
        dataslice = self.signal
        t_start = self.t_start
        # calculate the factor to align time / sampling rate units
        factor = factor_options.get("%s%s" % (self.t_start__unit.lower(), \
            self.sampling_rate__unit.lower()), 1.0)
        s_index = start_index
        if not s_index: s_index = 0
        e_index = end_index or (len(dataslice) - 1)
        if start_time:
            s_index = int(round(self.sampling_rate * (start_time - t_start) * factor))
        if end_time:
            e_index = int(round(self.sampling_rate * (end_time - t_start) * factor))
        if duration:
            if start_time or start_index:
                e_index = s_index + int(round(self.sampling_rate * duration * factor))
            else:
                s_index = e_index - int(round(self.sampling_rate * duration * factor))
        if samples_count:
            if start_time or start_index:
                e_index = s_index + samples_count
            else:
                s_index = e_index - samples_count
        if s_index >= 0 and s_index < e_index and e_index < len(dataslice):
            dataslice = dataslice[s_index:e_index+1]
            t_start = (s_index * 1.0 / self.sampling_rate * 1.0 / factor) # compute new t_start
        else:
            raise IndexError("Index is out of range. From the values provided \
we can't get the slice of the signal. We calculated the start index as %d and \
end index as %d. The whole signal has %d datapoints." % (s_index, e_index, \
len(dataslice)))
        if downsample and downsample < len(dataslice):
            dataslice = signal.resample(np.array(dataslice), downsample).tolist()
        return dataslice, t_start

    @apply
    def signal():
        def fget(self):
            return _data_as_list(self.signal_data)
        def fset(self, arr):
            self.signal_data = _clean_csv(arr)
        def fdel(self):
            pass
        return property(**locals())

    @property
    def size(self):
        return self.signal_size

    @property
    def is_alone(self):
        """
        Indicates whether to show an object alone, even if it is organized in
        an AnalogSignalArray. 
        """
        return (self.analogsignalarray.count() == 0)

    def save(self, *args, **kwargs):
        # override save to keep signal size up to date
        self.signal_size = len(self.signal) * 24            
        super(AnalogSignal, self).save(*args, **kwargs)


# 13 (of 15)
class IrSaAnalogSignal(BaseInfo):
    """
    NEO IrSaAnalogSignal @ G-Node.
    """
    # NEO attributes
    name = models.CharField('name', max_length=name_max_length)
    t_start = models.FloatField('t_start')
    t_start__unit = fmodels.TimeUnitField('t_start__unit', default=def_time_unit)
    # NEO relationships
    segment = models.ForeignKey(Segment, blank=True, null=True)
    recordingchannel = models.ForeignKey(RecordingChannel, blank=True, null=True)
    # NEO data arrays
    signal_data = models.TextField('signal_data') # use 'signal' property to get data
    signal__unit = fmodels.SignalUnitField('signal__unit', default=def_data_unit)
    times_data = models.TextField('times_data', blank=True) # use 'times' property to get data
    times__unit = fmodels.TimeUnitField('times__unit', default=def_time_unit)
    object_size = models.IntegerField('object_size', blank=True) # in bytes, for better performance

    def get_slice(self, start_time=None, end_time=None, start_index=None,\
            end_index=None, duration=None, samples_count=None, downsample=None):
        """
        Implements dataslicing/downsampling. Floats/integers are expected.
        'downsample' parameter defines the new resampled resolution.
        """
        dataslice = self.signal
        t_start = self.t_start
        times = self.times
        # calculate the factor to align time / sampling rate units
        #factor = factor_options.get("%s%s" % (self.t_start__unit.lower(), \
        #    self.sampling_rate__unit.lower()), 1.0)
        s_index = start_index
        if not s_index: s_index = 0
        e_index = end_index or (len(dataslice) - 1)
        if start_time: # TODO
            s_index = _find_nearest(np.array(times), start_time)
        if end_time: # TODO
            e_index = _find_nearest(np.array(times), end_time)
        if duration:
            if start_time:
                e_index = _find_nearest(np.array(times), start_time + duration)
            if start_index:
                e_index = _find_nearest(np.array(times), times[start_index] + duration)
            if end_time:
                e_index = _find_nearest(np.array(times), start_time - duration)
            if end_index:
                e_index = _find_nearest(np.array(times), times[end_index] - duration)
        if samples_count:
            if start_time or start_index:
                e_index = s_index + samples_count
            else:
                s_index = e_index - samples_count
        if s_index >= 0 and s_index < e_index and e_index < len(dataslice):
            dataslice = dataslice[s_index:e_index+1]
            times = times[s_index:e_index+1]
            t_start = times[0] # compute new t_start
        else:
            raise IndexError("Index is out of range. From the values provided \
we can't get the slice of the signal. We calculated the start index as %d and \
end index as %d. The whole signal has %d datapoints." % (s_index, e_index, \
len(dataslice)))
        if downsample and downsample < len(dataslice):
            dataslice = signal.resample(np.array(dataslice), downsample).tolist()
            times = signal.resample(np.array(times), downsample).tolist()
        return dataslice, times, t_start


    @apply
    def signal():
        def fget(self):
            return _data_as_list(self.signal_data)
        def fset(self, arr):
            self.signal_data = _clean_csv(arr)
        def fdel(self):
            pass
        return property(**locals())

    @apply
    def times():
        def fget(self):
            return _data_as_list(self.times_data)
        def fset(self, arr):
            self.times_data = _clean_csv(arr)
        def fdel(self):
            pass
        return property(**locals())

    @property
    def size(self):
        return self.object_size

    def save(self, *args, **kwargs):
        # override save to keep signal size up to date
        self.object_size = (len(self.signal) * 24) + \
            (len(self.times) * 24)
        super(IrSaAnalogSignal, self).save(*args, **kwargs)

    def full_clean(self, *args, **kwargs):
        """
        Add some validation to keep 'signal' and 'times' dimensions consistent.
        """
        if not len(self.signal) == len(self.times):
            raise ValidationError({"Data Inconsistent": meta_messages["data_inconsistency"]})
        super(IrSaAnalogSignal, self).full_clean(*args, **kwargs)

# 14 (of 15)
class Spike(BaseInfo):
    """
    NEO Spike @ G-Node.
    """
    # NEO attributes
    time = models.FloatField('t_start')
    time__unit = fmodels.TimeUnitField('time__unit', default=def_time_unit)
    sampling_rate = models.FloatField('sampling_rate')
    sampling_rate__unit = fmodels.SamplingUnitField('sampling_rate__unit', default=def_samp_unit)
    left_sweep = models.FloatField('left_sweep', default=0.0)
    left_sweep__unit = fmodels.TimeUnitField('left_sweep__unit', default=def_time_unit)
    # NEO relationships
    segment = models.ForeignKey(Segment, blank=True, null=True)
    unit = models.ForeignKey(Unit, blank=True, null=True)

    @property
    def size(self):
        return int(np.array([w.size for w in self.waveform_set.all()]).sum())

# 15 (of 15)
class WaveForm(BaseInfo):
    """
    Supporting class for Spikes and SpikeTrains.
    """
    channel_index = models.IntegerField('channel_index', null=True, blank=True)
    time_of_spike_data = models.FloatField('time_of_spike_data', default=0.0) # default used when WF is related to a Spike
    time_of_spike__unit = fmodels.TimeUnitField('time_of_spike__unit', default=def_data_unit)
    waveform_data = models.TextField('waveform_data')
    waveform__unit = fmodels.SignalUnitField('waveform__unit', default=def_data_unit)
    waveform_size = models.IntegerField('waveform_size', blank=True, null=True) # in bytes, for better performance
    spiketrain = models.ForeignKey(SpikeTrain, blank=True, null=True)
    spike = models.ForeignKey(Spike, blank=True, null=True)

    @apply
    def waveform():
        def fget(self):
            return _data_as_list(self.waveform_data)
        def fset(self, arr):
            self.waveform_data = _clean_csv(arr)
        def fdel(self):
            pass
        return property(**locals())

    @property
    def size(self):
        return self.waveform_size

    def save(self, *args, **kwargs):
        # override save to keep signal size up to date
        self.waveform_size = len(self.waveform) * 24
        super(WaveForm, self).save(*args, **kwargs)

# supporting functions
#===============================================================================

meta_classnames = {
    "block": Block,
    "segment": Segment,
    "event": Event,
    "eventarray": EventArray,
    "epoch": Epoch,
    "epocharray": EpochArray,
    "unit": Unit,
    "spiketrain": SpikeTrain,
    "analogsignal": AnalogSignal,
    "analogsignalarray": AnalogSignalArray,
    "irsaanalogsignal": IrSaAnalogSignal,
    "spike": Spike,
    "recordingchannelgroup": RecordingChannelGroup,
    "recordingchannel": RecordingChannel}

