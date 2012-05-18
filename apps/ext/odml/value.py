import types
class Value(object):
    """
    An odML value
    
    value
        mandatory (unless data is set). It's the string representation of the value.
    
    data
        mandatory (unless value is set). It's the content itself.
        (see the data and value attributes of this object)
    
    uncertainty (optional)
        an estimation of the value's uncertainty.
    
    unit (optional)
        the value's unit
    
    dtype (optional)
        the data type of the value

    id (optional)
        an external reference number (e.g. entry in a database)
    
    defaultFileName (optional)
        the default file name which should be used when saving the object
    
    definition
        optional, here additional comments on the value of the property can be given
        
    TODO: comment
    """
    def __init__(self, value=None, data=None, uncertainty=None, unit=None, dtype=None, definition=None, id=None, defaultFileName=None, comment=None):
        if data is None and value is None:
            raise TypeError("either data or value has to be set")
        if data is not None and value is not None:
            raise TypeError("only one of data or value can be set")
        
        self._dtype  = dtype
        self._property = None        
        self._unit = unit
        self._uncertainty = uncertainty
        self._dtype = dtype
        self._definition = definition
        self._id = id
        self._defaultFileName = defaultFileName
        self._comment = comment
        
        if value is not None:
            # assign value directly (through property would raise a change-event)
            self._value  = types.get(value, self._dtype)
        elif data is not None:
            self._value = data


    def __repr__(self):
        if self._dtype:
            return "<%s %s>" % (str(self._dtype), str(self._value))
        return "<%s>" % str(self._value)


    @apply
    def data():
        """
        used to access the raw data of the value
        (i.e. a datetime-object if dtype is "datetime")
        see also the value attribute
        """
        def fget(self):
            return self._value
        def fset(self, new_value):
            self._value = new_value
        return property(**locals())

    @apply
    def value():
        """
        used to access typed data of the value as a string.
        Use data to access the raw type, i.e.:
        
        >>> v = Value("1", type="float")
        >>> v.data
        1.0
        >>> v.data = 1.5
        >>> v.value
        "1.5"
        >>> v.value = 2
        >>> v.data
        2.0
        """  
        def fget(self):
            return types.set(self._value, self._dtype)
        def fset(self, new_value):
            self._value = types.get(new_string, self._dtype)
        return property(**locals())

    @apply
    def dtype():
        """
        the data type of the value
        
        If the data type is changed, it is tried, to convert the value to the new type.
        
        If this doesn't work, the change is refused.
        This behaviour can be overridden by directly accessing the *_dtype* attribute
        and adjusting the *data* attribute manually.
        """ 
        def fget(self):
            return self._dtype
        def fset(self, new_type):
            # check if this is a valid type
            if not types.valid_type(new_type):
                raise AttributeError("'%s' is not a valid type." % (new_type))
            # we convert the value if possible
            old_type  = self._dtype
            old_value = types.set(self._value, self._dtype)
            try:
                new_value = types.get(old_value,  new_type)
            except: # cannot convert, try the other way around
                try:
                    old_value = types.set(self._value, new_type)
                    new_value = types.get(old_value,   new_type)
                except: #doesn't work either, therefore refuse
                    raise ValueError("cannot convert '%s' from '%s' to '%s'" % (self.value, old_type, new_type))
            self._value = new_value
            self._dtype = new_type
        return property(**locals())

    @apply
    def uncertainty():
        def fget(self):
            return self._uncertainty
        def fset(self, new_value):
            self._uncertainty = new_value
        return property(**locals())

    @apply
    def unit():
        def fget(self):
            return self._unit
        def fset(self, new_value):
            self._unit = new_value
        return property(**locals())

    @apply
    def id():
        def fget(self):
            return self._id
        def fset(self, new_value):
            self._id = new_value
        return property(**locals())

    @apply
    def definition():
        def fget(self):
            return self._definition
        def fset(self, new_value):
            self._definition = new_value
        return property(**locals())

    @apply
    def comment():
        def fget(self):
            return self._comment
        def fset(self, new_value):
            self._comment = new_value
        return property(**locals())
 
    @apply
    def default_filename():
        def fget(self):
            return self._default_filename
        def fset(self, new_value):
            self._default_filename = new_value
        return property(**locals())


