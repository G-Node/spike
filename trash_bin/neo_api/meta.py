meta_messages = {
    "invalid_neo_id": "The NEO_ID provided is wrong and can't be parsed. The NEO_ID should have a form 'neo-object-type_object-ID', like 'segment_12345'. Here is the list of NEO object types supported: 'block', 'segment', 'event', 'eventarray', 'epoch', 'epocharray', 'unit', 'spiketrain', 'analogsignal', 'analogsignalarray', 'irsaanalogsignal', 'spike', 'recordingchannelgroup', 'recordingchannel'. Please correct NEO_ID and send the request again.",
    "wrong_neo_id": "The object with the NEO_ID provided does not exist.",
    "missing_neo_id": "For this type of request you should provide NEO_ID. The NEO_ID should have a form 'neo-object-type_object-ID', like 'segment_12345'. Please include NEO_ID and send the request again.",
    "invalid_method": "This URL does not support the method specified.",
    "invalid_obj_type": "You provided an invalid NEO object type parameter, or this parameter is missing. Here is the list of NEO object types supported: 'block', 'segment', 'event', 'eventarray', 'epoch', 'epocharray', 'unit', 'spiketrain', 'analogsignal', 'analogsignalarray', 'irsaanalogsignal', 'spike', 'recordingchannelgroup', 'recordingchannel'. Please correct the type and send the request again.",
    "missing_parameter": "Parameters, shown above, are missing. We need these parameters to proceed with the request.",
    "bad_parameter": "Some of the parameters provided are incorrect. Please consider values below:",
    "wrong_parent": "A parent object with this neo_id does not exist: ",
    "debug": "Debugging message.",
    "dict_required": "The following parameter must be of a type dict containing 'data' and 'units' keys: ",
    "no_enquery_related": "There are no related attributes for this object.",
    "not_authenticated": "Please authenticate before sending the request.",
    "not_authorized": "You don't have permissions to access the object.",
    "authenticated": "Successfully authenticated.",
    "invalid_credentials": "The credentials provided not valid.",
    "data_missing": "Some of the required parameters are missing: 'data', 'units' or 'channel_index'.",
    "units_missing": "You need to specify units (for example, 'ms' or 'mV') for following parameters.",
    "not_iterable": "Parameter must be of type 'list'",
    "bad_float_data": "The data given is not a list of comma-separated float / integer values. Please check your input.",
    "object_created": "Object created successfully.",
    "object_updated": "Object updated successfully. Data changes saved.",
    "object_selected": "Here is the list of requested objects.",
    "data_parsing_error": "Data, sent in the request body, cannot be parsed. Please ensure, the data is sent in JSON format.",
    "data_inconsistency": "The dimensions of the data provided do not match.",
    "wrong_params": "Parameters provided are incorrect. Please consider details in the 'details' element.",
    "retrieved": "Object retrieved successfully.",
    "no_objects_found": "No objects found.",
    "not_found": "The page you requested was not found.",
}

meta_objects = ("block", "segment", "event", "eventarray", "epoch", "epocharray", \
    "unit", "spiketrain", "analogsignal", "analogsignalarray", \
    "irsaanalogsignal", "spike", "recordingchannelgroup", "recordingchannel")

# attribute name. underscore indicates whether attribute is mandatory
meta_attributes = {
    "block": ('_name', 'filedatetime', 'index'),
    "segment": ('_name', 'filedatetime', 'index'),
    "event": ('_label',),
    "eventarray": (),
    "epoch": ('_label',),
    "epocharray": (),
    "unit": ('_name',),
    "spiketrain": (),
    "analogsignal": ('_name',),
    "analogsignalarray": (),
    "irsaanalogsignal": ('_name',),
    "spike": (),
    "recordingchannelgroup": ('_name',),
    "recordingchannel": ('_name', 'index')}

# possible unit types: order matters!!
meta_unit_types = {
    "time": ("s", "ms", "mcs"), # *1000, *1, /1000
    "signal": ("v", "mv", "mcv"),
    "sampling": ("hz", "khz", "mhz", "1/s")} # *1, *1000, *100000, *1

# object type: data-related attributes names. waveform is a special case (2-3D).
meta_data_attrs = {
    "event": ('time',),
    "epoch": ('time', 'duration'),
    "spiketrain": ('t_start', 't_stop', 'times', 'waveforms'),
    "analogsignal": ('sampling_rate', 't_start', 'signal'),
    "irsaanalogsignal": ('t_start', 'signal', 'times'),
    "spike": ('left_sweep', 'time', 'sampling_rate', 'waveforms')}

# object type: parent objects
meta_parents = {
    "segment": ('block',),
    "eventarray": ('segment',),
    "event": ('segment','eventarray'),
    "epocharray": ('segment',),
    "epoch": ('segment','epocharray'),
    "recordingchannelgroup": ('block',),
    "recordingchannel": ('recordingchannelgroup',),
    "unit": ('recordingchannel',), # this object is special. do not add more parents
    "spiketrain": ('segment','unit'),
    "analogsignalarray": ('segment',),
    "analogsignal": ('segment','analogsignalarray','recordingchannel'),
    "irsaanalogsignal": ('segment','recordingchannel'),
    "spike": ('segment','unit')}

# object type + children
meta_children = {
    "block": ('segment','recordingchannelgroup'),
    "segment": ('analogsignal', 'irsaanalogsignal', 'analogsignalarray', 'spiketrain', 'spike', 'event', 'eventarray', 'epoch', 'epocharray'),
    "eventarray": ('event',),
    "epocharray": ('epoch',),
    "recordingchannelgroup": ('recordingchannel','analogsignalarray'),
    "recordingchannel": ('unit','analogsignal', 'irsaanalogsignal'),
    "unit": ('spiketrain','spike'), 
    "analogsignalarray": ('analogsignal',)}

# allowed parameters for GET for data slicing
allowed_range_params = {
    'start_time': lambda x: float(x),
    'end_time': lambda x: float(x),
    'start_index': lambda x: int(x),
    'end_index': lambda x: int(x),
    'duration': lambda x: float(x),
    'samples_count': lambda x: int(x),
    'downsample': lambda x: int(x),
}

# factors to align time / sampling rate units for Analog Signals
factor_options = {
  "skhz": 1000.0,
  "smhz": 1000000.0,
  "mshz": 1.0/1000.0,
  "msmhz": 1000.0,
  "mcshz": 1.0/1000000.0,
  "mcskhz": 1.0/1000.0,
}


