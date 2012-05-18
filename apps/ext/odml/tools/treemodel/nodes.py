"""
provides node functionality for the eventable odml types
Document, Section, Property and Value

additionally implements change notifications up to the corresponding section
"""
from .. import event

class RootNode(object):
    @property
    def children(self):
        return self._sections
        
    def from_path(self, path):
        child = self.children[path[0]]
        if len(path) == 1:
            return child
        return child.from_path(path[1:])

    def to_path(self):
        return ()
    
    def path_to(self, child):
        """return the path from this node to its direct child *child*"""
        return (self._sections.index(child),)

class ParentedNode(RootNode):
    def to_path(self):
        return self.parent.to_path() + self.parent.path_to(self)
    
    def successor(self):
        return self.parent.children[self.position + 1]
    
    def next(self):
        """
        returns the next section following in this section's parent's list of sections
        returns None if there is no further element available

        i.e.:
            parent
              sec-a (<- self)
              sec-b

        will return sec-b
        """
        try:
            return self.successor()
        except IndexError:
            return None
    
    @property
    def position(self):
        return self.parent.path_to(self)[-1]
        
    @property
    def parent(self):
        return self._parent

class SectionNode(ParentedNode):
    """
    SectionNodes are special as they wrap two types of sub-nodes:
    
    * SubSections (path = (0, idx))
    * Properties  (path = (1, idx))
    """
    def from_path(self, path):
        assert len(path) > 1
        
        if path[0] == 0: # sections
            return super(SectionNode, self).from_path(path[1:])
        
        # else: properties
        child = self._props[path[1]]

        if len(path) == 2:
            return child
        return child.from_path(path[2:])
        
    
    def path_to(self, child):
        if isinstance(child, event.Property):
            return (1, self._props.index(child))
        return (0, self._sections.index(child))

        
class PropertyNode(ParentedNode):
    @property
    def parent(self):
        """returns the parent section of this Property"""
        return self._section
    
    @property
    def children(self):
        return self._values
    
    def successor(self):
        return self.parent._props[self.position + 1]
    
    def path_to(self, child):
        return (self.values.index(child),)

class ValueNode(ParentedNode):
    @property
    def parent(self):
        return self._property
    
    def path_from(self, path):
        raise TypeError("Value objects have no children")
    
    def path_to(self, child):
        raise TypeError("Value objects have no children")

#TODO? provide this externally?
class Document(event.Document, RootNode): pass
class Value(event.Value, ValueNode): pass
class Property(event.Property, PropertyNode): pass
class Section(event.Section, SectionNode): pass

def on_value_change(value, **kwargs):
    prop = value._property
    if prop is not None:
        prop._Changed(prop, value=value, value_pos=value.position, **kwargs)
    
Value._Changed += on_value_change

def on_property_change(prop, **kwargs):
    sec = prop._section
    if sec is not None:
        sec._Changed(sec, prop=prop, prop_pos=prop.position, **kwargs)
    
Property._Changed += on_property_change

# TODO on_section_change(sec, **kwargs)
