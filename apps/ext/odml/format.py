"""
A module providing general format information
and mappings of xml-attributes to their python class equivalents
"""

from . import doc, section, property, value

class Format(object):
    _map = {}
    _rev_map = None
    
    def map(self, name):
        return self._map.get(name, name)
    def revmap(self, name):
        if self._rev_map is None:
            # create the reverse map only if requested
            self._rev_map = {}
            for k,v in self._map.iteritems():
                self._rev_map[v] = k
        return self._rev_map.get(name, name)

class Value(Format):
    _name = "value"
    _args = {
        'value': 0,
        'uncertainty': 0,
        'unit': 0,
        'type': 0,
        'definition': 0,
        'id': 0,
        'defaultFileName': 0
        }
    _map = {'type': 'dtype'}
    
class Property(Format):
    _name = "property"
    _args = {
        'name': 1,
        'value': 1,
        'synonym': 0,
        'definition': 0,
        'mapping': 0,
        'dependency': 0,
        'dependencyValue': 0
        }
    _map = {'value': 'values'}

class Section(Format):
    _name = "section"
    _args = {
        'type': 1,
        'name': 0,
        'definition': 0,
        'id': 0,
        'link': 0,
        'repository': 0,
        'mapping': 0,
        'section': 0,
        'property': 0
        }
    _map = {
        'section': 'sections',
        'property': 'properties',
        }

class Document(Format):
    _name = "odML"
    _args = {
        'version': 0,
        'author': 0,
        'date': 0,
        'section': 0,
        'repository': 0,
        }
    _map = {
        'section': 'sections'
        }

Document = Document()
Section  = Section()
Value    = Value()
Property = Property()

elements = {
    doc.Document:      Document,
    section.Section:   Section,
    property.Property: Property,
    value.Value:       Value
    }
    

__all__ = [Document, Section, Property, Value, elements]
