# 1
block = {
    "obj_type": "block",
    "name": "Block of recordings from May, 10",
    "filedatetime": "2011-10-05",
    "index": 1}

# 2
segment = {
    "obj_type": "segment",
    "name": "Trial 1",
    "filedatetime": "2011-10-07",
    "index": 1,
    "block": "block_1"}

# 3
eventarray = {
    "obj_type": "eventarray",
    "segment": "segment_1"}

# 4
event = {
    "obj_type": "event",
    "time": {
        "data": 7.22,
        "units": "ms"
    },
    "label": "Stimuli end",
    "segment": "segment_1",
    "eventarray": "eventarray_1"}

# 5
epocharray = {
    "obj_type": "epocharray",
    "segment": "segment_1"}

# 6
epoch = {
    "obj_type": "epoch",
    "time": {
        "data": 78.22,
        "units": "ms"
    },
    "duration": {
        "data": 0.35,
        "units": "ms"
    },
    "label": "Displaying blue screen",
    "segment": "segment_1",
    "epocharray": "epocharray_1"}

# 7
recordingchannelgroup = {
    "obj_type": "recordingchannelgroup",
    "name": "Tethrode #5",
    "block": "block_1"}

# 8
recordingchannel = {
    "obj_type": "recordingchannel",
    "name": "Electrode #1",
    "index": 1,
    "recordingchannelgroup": "recordingchannelgroup_1"}

# 9
unit = {
    "obj_type": "unit",
    "name": "Neuron 34.56 x 28.8 x 245.69",
    "recordingchannel": [
        "recordingchannel_1"
    ]}

# 10
analogsignalarray = {
    "obj_type": "analogsignalarray",
    "segment": "segment_1"}

# 11
analogsignal = {
    "obj_type": "analogsignal",
    "name": "AS-1",
    "sampling_rate": {
        "data": 20000,
        "units": "Hz"
    },
    "t_start": {
        "data": 0.0,
        "units": "ms"
    },
    "signal": {
        "units": "mV", 
        "data": [12.2, 12.7, 19.0, 7.81, 3.42, 9.28, -5.86]
    },
    "segment": "segment_1",
    "recordingchannel": "recordingchannel_1"}

# 12
irsaanalogsignal = {
    "obj_type": "irsaanalogsignal",
    "name": "ISAS-1",
    "t_start": {
        "data": -200.0,
        "units": "ms"
    },
    "signal": {
        "units": "mV", 
        "data": [12.2, 12.7, 19.0, 7.81, 3.42, 9.28, -5.86]
    },
    "times": {
        "units": "ms", 
        "data": [155.0, 158.0, 160.0, 161.0, 162.0, 165.0, 168.0]
    },
    "segment": "segment_1",
    "recordingchannel": "recordingchannel_1"}

# 13
spike = {
    "obj_type": "spike",
    "time": {
        "data": 300.0,
        "units": "ms"
    },
    "sampling_rate": {
        "data": 20.0,
        "units": "kHz"
    },
    "left_sweep": {
        "data": 15.0,
        "units": "ms"
    },
    "waveforms": [{
            "channel_index": 0,
            "waveform": {
                "units": "mV", 
                "data": [5.86, -1.46, -0.488, -7.32, -9.77, -12.7, -12.7]
            }
        },
        {
            "channel_index": 1,
            "waveform": {
                "units": "mV", 
                "data": [45.86, -31.46, -0.338, 67.32, -19.77, -109.7, -39.7]
            }
    }],
    "segment": "segment_1",
    "unit": "unit_1"}

# 14
spiketrain = {
    "obj_type": "spiketrain",
    "t_start": {
        "data": -400.0,
        "units": "ms"
    },
    "t_stop": {
        "data": 800.0,
        "units": "ms"
    },
    "times": {
        "units": "ms", 
        "data": [-4.88, 3.42, 2.44]
    },
    "waveforms": [{
            "channel_index": 0,
            "time_of_spike": {
                "units": "ms",
                "data": 469.1
            },
            "waveform": {
                "units": "mV", 
                "data": [5.86, -1.46, -0.488, -7.32, -9.77, -12.7, -12.7]
            }
        },
        {
            "channel_index": 1,
            "time_of_spike": {
                "units": "ms",
                "data": 789.4
            },
            "waveform": {
                "units": "mV", 
                "data": [45.86, -31.46, -0.338, 67.32, -19.77, -109.7, -39.7]
            }
    }],
    "segment": "segment_1",
    "unit": "unit_1"
}

sample_objects = {
    "block": block,
    "segment": segment,
    "event": event,
    "eventarray": eventarray,
    "epoch": epoch,
    "epocharray": epocharray,
    "unit": unit,
    "spiketrain": spiketrain,
    "analogsignal": analogsignal,
    "analogsignalarray": analogsignalarray,
    "irsaanalogsignal": irsaanalogsignal,
    "spike": spike,
    "recordingchannelgroup": recordingchannelgroup,
    "recordingchannel": recordingchannel
}
