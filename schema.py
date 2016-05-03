import re

from schema_violation import *
from datatypes import *

schema_id_pat = re.compile(r'^(?i)[a-f0-9]{8}-?([a-f0-9]{4}-?){3}[a-f0-9]{12}$')
schema_version_pat = re.compile(r'^(?i)\d+(\.\d+){0,2}(-[-_a-z]+)?$')


class schema:
    def __init__(self, name, node_from_schema_yaml, parent=None):
        self.name = name
        self.parent = None
        if parent:
            self.parent = parent
        else:
            self._node_root = node_from_schema_yaml            
        self.node = node_from_schema_yaml
        
    def get_xpath(self):
        if self.parent:
            return '%s/%s' % (self.parent().get_xpath(), self.name)
        else:
            return 'schema:%s' % self.name
        
    def children(self):
        node = self.node
        if not hasattr(node, 'children'):
            return
        contains = node['children']
        for key, value in contains.iteritems():
            yield schema(key, value, self)

    def extra_schemas(self):
        node = self.node
        if not hasattr(node, 'contains'):
            return
        contains = node['contains']
        for key, value in contains.iteritems():
            yield schema(key, value, self)
            
    def has_def_for(self, keys):
        '''Does this schema have a definition for any key in a certain list?'''
        if is_string(keys):
            keys = [keys]
        for k in keys:
            if k in self.node:
                print('yes, schema has def for %s' % keys)
                return True
        print('no, schema doesnt have def for %s' % keys)
                   
    def get_expected_types(self):
        '''
        Return a description of the types that this schema expects/accepts.
        Normally this is a simple string, like 'str' or 'map'. However, it
        may be a name of another schema node (e.g., 'email' might refer to a
        node in the schema that defines email addresses), or it may be a list
        of allowed types, if several are possible--or it may be None if the
        schema imposes no constraints on the type of the yaml node it
        validates.
        '''
        if self.has_def_for('keys'): return 'map'
        if self.has_def_for('items'): return 'seq'
        if self.has_def_for('fields'): return 'tuple'
        if self.has_def_for('regex'): return 'str'
        if self.has_def_for('multiple_of'): return 'int'
        if self.has_def_for('type'): return self.node['type']
        if self.has_def_for('default'): return str(type(self.node['default']))
        if self.has_def_for(['max', 'min', 'xmax', 'xmin']): return ['int', 'float', 'date']
        if self.has_def_for('extras'): return ['map', 'seq', 'tuple']
        # If we get here, there are 2 possible semantics that might still obtain:
        # 1. We're a degenerate schema with a single string that describes an expected data type.
        # 2. We are a very unconstrained schema where the data type isn't guessable or
        #    enforceable.
        if is_string(self.node): return self.node
                    
    def validate(self, yaml_node, node_xpath='/'):
        '''
        Compare a node in a yaml doc/stream to a schema, and return a list of
        errors. An empty list means the yaml is valid according to the schema.
        '''
        errors = []
        expected = self.get_expected_types()
        actual = get_simple_type_name(yaml_node)
        if expected != actual:
            print('self.node = %s' % self.node)
            errors.append(schema_violation(self, node_xpath, 'Expected node type to be %s, not %s.' % (expected, actual)))
        return errors
