from property import Property

class Section(object):
    """A odML Section"""
    type       = None
    id         = None
    link       = None
    repository = None
    mapping    = None
    reference  = None # the *import* property

    def __init__(self, name, parent=None):
        self._name = name
        self._parent = parent
        self._sections = []
        self._props = []

    def __repr__(self):
        return "<Section %s (%d)>" % (self._name, len(self._sections))

    @apply
    def name():
        def fget(self):
            return self._name
        def fset(self, new_value):
            self._name = new_value
        return property(**locals())
        
    def get_name_definition(self, UseTerminology=True):
        if hasattr (self, "_name_definition"):
            return self._name_definition
        else:
            return None

    def set_name_definition(self, val):
        self._name_definition = val

    def del_name_definition(self):
        del self._name_definition

    definition = property(get_name_definition,
                              set_name_definition,
                              del_name_definition,
                              "Name Definition of the section")

    # API (public) 
    #
    #  properties
    @property
    def properties(self):
    	return self._props

    @property
    def sections(self):
    	return self._sections
    
    def append(self, obj):
        """append a Section or Property"""
        if isinstance(obj, Section):
            self._sections.append (obj)
            obj._parent = self
        elif isinstance(obj, Property):
            self._props.append (obj)
            obj._section = self
        else:
            raise ValueError, "Can only append sections and properties"

    def __iter__(self):
        """iterate over each section and property contained in this section"""
        for section in self._sections:
            yield section
        for prop in self._props:
            yield prop
