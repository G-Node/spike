from meta import meta_attributes, meta_data_attrs, meta_children, meta_parents, allowed_range_params
from datetime import datetime


def clean_attr(_attr):
    """
    By default attribute names in meta contain prefix "_" to indicate whether an 
    attribute is mandatory. This needs to be cleaned up before assigning to the
    NEO object.
    """
    if _attr.startswith("_"): return _attr[1:]
    return _attr


def json_builder(obj, GET={}, enquery="full"):
    """
    Builds a JSON response for a given object. Again, we "boycott" everything 
    which is "not done by our hands" by not using any json picklers for safety
    reasons. Method recursively iterates over the children when 'cascade' 
    parameter is provided in the request. Expects NEO-type object.
    """
    n = {} # future JSON response
    n["neo_id"] = obj.neo_id
    """ this variable is used to track whether at least some information exists 
    for the requested object. This is needed to raise an error when knowingly a
    non-existing information was requested, such as a parent of a block. 
    However, as this behaves unfriendly with cascade requests, this feature is
    switched off for the moment."""
    assigned = False
    if GET.has_key("q"):
        if GET["q"] in ("full", "info", "data", "parents", "children"):
            enquery = GET["q"]
    if enquery == "info" or enquery == "full":
        assigned = assign_attrs(n, obj) or assigned
    if enquery == "data" or enquery == "full":
        params = {} # these are params used to filter requested data
        for k, v in GET.items():
            if k in allowed_range_params.keys() and allowed_range_params.get(k)(v):
                params[str(k)] = allowed_range_params.get(k)(v)
        assigned = assign_data_arrays(n, obj, **params) or assigned
    if enquery == "parents" or enquery == "full":
        assigned = assign_parents(n, obj) or assigned
    if GET.get("cascade") or enquery == "children" or enquery == "full":
        """ here 
        - if cascade is provided, then we need to assign children and the 
        children container will contain json objects, not just ids;
        - if children is requested we obviously go here, and cascade also make
        sense
        - if there is a full enquery everything will be provided anyway
        """
        assigned = assign_children(n, obj, enquery, GET) or assigned
    assign_common(n, obj)
    return n
    #if assigned: return n # switched OFF, see comments above


def assign_attrs(json, obj):
    """
    Assigns attibutes from NEO to json object for later HTTP response.
    """
    json["size"] = getattr(obj, "size")
    for _attr in meta_attributes[obj.obj_type]:
        attr = clean_attr(_attr)
        value = getattr(obj, attr)
        if type(value) == type(datetime.now()):
            value = str(value) # datetime is not JSON serializable
        json[attr] = value
        if hasattr(obj, attr + "__unit"):
            json[attr + "__unit"] = getattr(obj, attr + "__unit")
    return True # we assume object always has a "size" attribute


def assign_data_arrays(json, obj, **params):
    """
    Assigns data-related attrs from NEO to json object for later HTTP response.
    """
    assigned = False
    if meta_data_attrs.has_key(obj.obj_type):
        for arr in meta_data_attrs[obj.obj_type]:
            if arr == "waveforms":
                array = []
                for wf in obj.waveform_set.all():
                    w = {
                        "channel_index": wf.channel_index,
                        "waveform": {
                            "data": wf.waveform,
                            "units": wf.waveform__unit
                        }
                    }
                    if obj.obj_type == "spiketrain":
                        w["time_of_spike"] = {
                            "data": wf.time_of_spike_data,
                            "units": wf.time_of_spike__unit
                        }
                    array.append(w)
            else: 
                data = getattr(obj, arr)
                array = {"data": data, "units": getattr(obj, arr + "__unit")}
            json[arr] = array
        if params: # need some slicing
            if obj.obj_type == "irsaanalogsignal":
                json["signal"]["data"], json["times"]["data"], \
                    json["t_start"]["data"] = obj.get_slice(**params)
            elif obj.obj_type == "analogsignal":
                json["signal"]["data"], json["t_start"]["data"] = obj.get_slice(**params)
        assigned = True
    return assigned
    

def assign_parents(json, obj):
    """
    Assigns parents from NEO to json object for later HTTP response.
    """
    assigned = False
    obj_type = obj.obj_type
    if meta_parents.has_key(obj_type):
        if obj_type == "unit":
            ids = []
            r = meta_parents[obj_type][0]
            parents = getattr(obj, r).all()
            for p in parents:
                ids.append(p.neo_id)
            json[r] = ids
        else:
            for r in meta_parents[obj_type]:
                parent = getattr(obj, r)
                if parent:
                    json[r] = parent.neo_id
                else:
                    json[r] = None
        assigned = True
    return assigned


def assign_children(json, obj, enquery, GET):
    """
    Assigns children from NEO to json object for later HTTP response. Able to
    make recursive retrieval when 'cascade' is provided.
    """
    assigned = False
    obj_type = obj.obj_type
    if meta_children.has_key(obj_type):
        for r in meta_children[obj_type]:
            if GET.get("cascade"): # retrieve objects recursively if cascade
                ch = [json_builder(o, GET, enquery) for o in \
                    getattr(obj, r + "_set").all()]
            else:
                ch = [o.neo_id for o in getattr(obj, r + "_set").all()]
            json[r] = ch
        assigned = True
    return assigned


def assign_common(json, obj):
    """
    Assigns common information from NEO to json object for later HTTP response.
    """
    json["author"] = obj.author.username
    json["date_created"] = str(obj.date_created)


