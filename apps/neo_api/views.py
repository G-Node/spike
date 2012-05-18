from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, get_host, HttpResponse, HttpResponseBadRequest
from django.template import RequestContext
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import condition

from neo_api.json_builder import *
from neo_api.models import *
from meta import *
try:
    import json
except ImportError:
    import simplejson as json
import jsonpickle
import re
import hashlib

#===============================================================================
# supporting functions

class BasicJSONResponse(HttpResponse):
    """
    This is a JSON response class, which expects a python dict from which it 
    will pickle a response. Sets up an appropriate Cont-Type. User and Message 
    always appreciated.
    """
    def __init__(self, json_obj={}, message_type=None, request=None):
        if request: 
            if request.user: json_obj["logged_in_as"] = request.user.username
        if message_type:
            json_obj["message_type"] = message_type
            json_obj["message"] = meta_messages[message_type]
        super(BasicJSONResponse, self).__init__(json.dumps(json_obj))
        self['Content-Type'] = "application/json"
        self['G-Node-Version'] = "1.0"

class Created(BasicJSONResponse):
    status_code = 201

class BadRequest(BasicJSONResponse):
    status_code = 400

class Unauthorized(BasicJSONResponse):
    status_code = 401

class NotFound(BasicJSONResponse):
    status_code = 404

class NotSupported(BasicJSONResponse):
    status_code = 405


def parse_neo_id(neo_id):
    """ Returns obj_type and obj_id or throws an error """
    mid = str(neo_id).find("_")
    if mid > 0 and len(neo_id) > mid + 1: # exclude error in case of "segment_"
        obj_type = neo_id[:neo_id.find("_")]
        obj_id  = neo_id[neo_id.find("_")+1:]
        return obj_type, obj_id
    raise TypeError("totally wrong NEO ID provided.")


def get_object(obj_type, obj_id, user):
    """ Returns requested object.
    Attention! This function returns HTTP response in case an exception occurs.
    """
    classname = meta_classnames[obj_type]
    try:
        obj = classname.objects.get(id=obj_id)
    except ObjectDoesNotExist:
        return BadRequest(json_obj={"neo_id": "%s_%s" % \
            (obj_type, obj_id)}, message_type="wrong_neo_id")
    if not obj.is_accessible(user):
        return Unauthorized(json_obj={"neo_id": "%s_%s" % \
            (obj_type, obj_id)}, message_type="not_authorized")
    return obj
    

def auth_required(func):
    """
    Decorator for views where authentication required. 
    Returns HTTP 403 Unauthorized if user is not authenticated.
    """
    argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
    fname = func.func_name
    def auth_func(*args, **kwargs):
        if not args[0].user.is_authenticated():
            return Unauthorized(message_type="not_authenticated")
        return func(*args, **kwargs)
    return auth_func


def check_obj_type(func):
    """ Decorator that checks the correct object type. """
    argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
    fname = func.func_name
    def auth_func(*args, **kwargs):
        if not kwargs["obj_type"] in meta_objects:
            return NotFound(message_type="not_found")
        return func(*args, **kwargs)
    return auth_func


def get_etag(request, obj_type, obj_id):
    """ A decorator to compute the ETags """
    obj = get_object(obj_type, obj_id, request.user)
    if isinstance(obj, HttpResponse):
        return None # some error while getting an object
    return hashlib.md5(str(obj.last_modified)).hexdigest()


def get_last_modified(request, obj_type, obj_id):
    """ A decorator to get the last modified datetime """
    obj = get_object(obj_type, obj_id, request.user)
    if isinstance(obj, HttpResponse):
        return None # some error while getting an object
    return obj.last_modified


#===============================================================================
# main views

@check_obj_type
@condition(etag_func=get_etag, last_modified_func=get_last_modified)
@auth_required
def handle_object(request, obj_type, obj_id):
    """
    GET: get, PUT/POST: update, DELETE: delete single NEO object. Serves partial
    data requests (info, data etc.) using GET params.
    """
    actions = {
        'GET': get_single,
        'PUT': create_or_update,
        'POST': create_or_update,
        'DELETE': delete}
    if request.method in actions.keys():
        obj = get_object(obj_type, obj_id, request.user)
        if isinstance(obj, HttpResponse):
            return obj # returns an error here
        response = actions[request.method](request, obj_type, obj)
    else:
        response = NotSupported(message_type="invalid_method", request=request)
    return response


@auth_required
@check_obj_type
def handle_category(request, obj_type):
    """
    GET: query all category, PUT/POST: create new
    Query params transmitted using GET params.
    """
    actions = {
        'GET': select,
        'PUT': create_or_update,
        'POST': create_or_update}
    if request.method in actions.keys():
        response = actions[request.method](request, obj_type)
    else:
        response = NotSupported(message_type="invalid_method", request=request)
    return response


def create_or_update(request, obj_type, obj=None):
    """
    This is a slave function to create or update a NEO object. We "boycott" 
    everything "that's not made by our hands" for security reasons (no automatic
    JSON parsing into NEO object). Create and update have very similar 
    functionality thus implemented as one huge function.
    """
    if obj: update = True
    else: update = False
    to_link, parents = None, None # handlers for special cases (waveforms, units)
    try:
        rdata = json.loads(request._get_raw_post_data())
    except ValueError:
        return BadRequest(message_type="data_parsing_error", request=request)

    # all POST requests should be of type dict
    if not type(rdata) == type({}):
        return BadRequest(message_type="data_parsing_error", request=request)

    if update: # this is update case
        message_type = "object_updated"
    else: # this is create case
        classname = meta_classnames[obj_type]
        obj = classname()
        message_type = "object_created"

    # processing attributes
    missing = [] # collector of missing attributes / data fields
    for _attr in meta_attributes[obj_type]:
        attr = clean_attr(_attr)
        obj_attr = None
        if rdata.has_key(attr):
            obj_attr = rdata[attr]
            setattr(obj, attr, obj_attr)
            if rdata.has_key(attr + "__unit"):
                obj_attr_unit = rdata[attr + "__unit"]
                setattr(obj, attr + "__unit", obj_attr_unit)
        elif _attr.startswith("_") and not update:
            missing.append(attr) # collect all missing attrs, raise 400 later 

    if not update:
        obj.author = request.user
    if rdata.has_key("datafile_id"):
        obj_attr = rdata["datafile_id"]
        # enable this when file integration is done TODO
        #obj.file_origin = Datafile.objects.get(id=datafile_id)

    # processing data-related attributes (data fields)
    if meta_data_attrs.has_key(obj_type):
        for data_attr in meta_data_attrs[obj_type]:
            if rdata.has_key(data_attr):
                if data_attr == "waveforms":
                    # Waveforms - it's a special case, 2-3D array. Parsing and update is made of 
                    # three stages: we create new waveforms first (no save), then delete old
                    # ones, then save and assign new waveforms to the host object.
                    waveforms = rdata[data_attr] # some processing is done later in this view
                    if not getattr(waveforms, "__iter__", False):
                        return BadRequest(message_type = "not_iterable", request=request)
                    to_link = [] # later this list is used to link waveforms to the obj
                    for wf in waveforms:
                        try:
                            w = WaveForm()
                            try:
                                w.channel_index = wf["channel_index"]
                                w.waveform = wf["waveform"]["data"]
                                w.waveform__unit = wf["waveform"]["units"]
                                w.author = request.user
                                if obj_type == "spiketrain":
                                    w.time_of_spike_data = wf["time_of_spike"]["data"]
                                    w.time_of_spike__unit = wf["time_of_spike"]["units"]
                                to_link.append(w)
                            except KeyError:
                                return BadRequest(message_type="data_missing", request=request)
                            except ValueError, v:
                                return BadRequest(json_obj={"details": v.message}, \
                                    message_type = "bad_float_data", request=request)
                        except AttributeError, TypeError:
                            return BadRequest(json_obj={"element": data_attr}, \
                                message_type="dict_required", request=request)
                else:
                    attr = rdata[data_attr]
                    # some checks
                    if not (type(attr) == type({})):
                        return BadRequest(json_obj={"element": data_attr}, \
                            message_type="dict_required", request=request)
                    if not attr.has_key("data"):
                        return BadRequest(message_type="data_missing", \
                            request=request)
                    try: # for data parsing see class methods / decorators
                        setattr(obj, data_attr, attr["data"])
                    except ValueError, v:
                        return BadRequest(json_obj={"details": v.message}, \
                            message_type="bad_float_data", request=request)
                    # processing attribute data units
                    if attr.has_key("units"):
                        attr_unit = attr["units"]
                        setattr(obj, data_attr + "__unit", attr_unit)
                    else:
                        # units are required
                        return BadRequest(json_obj={"element": data_attr}, \
                            message_type="units_missing", request=request)
            elif not update:
                missing.append(data_attr) # collect all missing attrs, raise 400 later 

    if missing: # return bad request if required attrs / fields are missing
        return BadRequest(json_obj={"missing": missing}, \
            message_type="missing_parameter", request=request)

    # processing relationships
    if meta_parents.has_key(obj_type):
        if obj_type == "unit":
            # unit is a special case. there may be several parents in one parameter.
            r = meta_parents[obj_type][0]
            if rdata.has_key(r):
                parent_ids = rdata[r]
                if not getattr(parent_ids, "__iter__", False):
                    return BadRequest(json_obj={"element": r}, \
                        message_type="not_iterable", request=request)
                parents = []
                for p in parent_ids: # this looks ugly.
                    try:
                        o_t, o_i = parse_neo_id(p)
                    except Exception, e:
                        return BadRequest(json_obj={"neo_id": str(p)}, 
                            message_type="invalid_neo_id")
                    parent = get_object(o_t, o_i, request.user)
                    if isinstance(parent, HttpResponse):
                        return parent
                    parents.append(parent) # some processing done later in this view
        else:
            for r in meta_parents[obj_type]:
                if rdata.has_key(r):
                    try:
                        o_t, o_i = parse_neo_id(rdata[r])
                    except Exception, e:
                        return BadRequest(json_obj={"neo_id": str(rdata[r])}, 
                            message_type="invalid_neo_id")
                    parent = get_object(o_t, o_i, request.user)
                    if isinstance(parent, HttpResponse):
                        return parent
                    setattr(obj, r, parent)

    # catch exception if any of values provided do not match
    try:
        obj.full_clean()
    except ValidationError, VE:
        return BadRequest(json_obj=VE.message_dict, \
            message_type="bad_parameter", request=request)

    # processing (almost) done
    obj.save()

    # process complex cases: waveforms, unit
    # this save() and delete() operations can be earliest done here, to exclude 
    # the case of creating and saving the whole object before facing an error
    if to_link:
        for wf in obj.waveform_set.all(): # remove old waveforms, if exist
            wf.delete()
        for wf in to_link: # assign and save new waveforms
            setattr(wf, obj_type, obj)
            wf.save()
    if obj_type == "unit" and parents:
        setattr(obj, r, parents)
        obj.save()

    request.method = "GET"
    #request.GET["q"] = "info"
    return get_single(request, obj.obj_type, obj, message_type, not update)


def get_single(request, obj_type, obj, message_type="retrieved", new=False):
    """
    This is a slave function to get a single NEO object by given NEO_ID. Due to 
    security reasons we do full manual reconstruction of the JSON object from 
    its django brother.
    """
    try:
        n = json_builder(obj, request.GET)
    except ValueError, e:
        return BadRequest(json_obj={"details": e.message}, \
            message_type="wrong_params", request=request)
    except IndexError, e:
        return BadRequest(json_obj={"details": e.message}, \
            message_type="wrong_params", request=request)
    if not n:
        return BadRequest(message_type="no_enquery_related", request=request)
    if new: return Created(json_obj=n, message_type=message_type, request=request)
    return BasicJSONResponse(json_obj=n, message_type=message_type, request=request)


def select(request, obj_type):
    """ Returns a list of object of the same NEO type. """
    if obj_type in meta_objects:
        classname = meta_classnames[obj_type]
        # TODO add some filtering, sorting etc. here
        objects = classname.objects.filter(author=request.user)[:1000] #FIXME
        if objects:
            selected = [o.neo_id for o in objects]
            message_type = "object_selected"
        else:
            selected = None
            message_type = "no_objects_found"
        resp_data = {
            "selected": selected,
            "object_total": len(objects),
            "object_selected": len(objects),
            "selected_as_of": 0
        }
        return BasicJSONResponse(resp_data, message_type, request)
    else:
        return BadRequest(message_type="invalid_obj_type", request=request)


def delete(request, neo_id):
    """
    This is a slave function to delete a NEO object by given NEO_ID.
    """
    pass


def process(request):
    """ DEPRECATED """
    pass

