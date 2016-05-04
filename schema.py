import re

from schema_violation import *
from datatypes import *

schema_id_pat = re.compile(r'^(?i)[a-f0-9]{8}-?([a-f0-9]{4}-?){3}[a-f0-9]{12}$')
schema_version_pat = re.compile(r'^(?i)\d+(\.\d+){0,2}(-[-_a-z]+)?$')

_not_yet_inited = 'nOt yEt iNiTeD'


class schema:
    def __init__(self, name, node_from_schema_yaml, parent=None):
        self.name = name
        self.parent = None
        if parent:
            self.parent = parent
        else:
            self._node_root = node_from_schema_yaml            
        self.node = node_from_schema_yaml
        self._expected_types = _not_yet_inited
        self._regex = _not_yet_inited
        
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
        if not is_map(self.node): return False
        if is_string(keys):
            keys = [keys]
        for k in keys:
            if k in self.node:
                return True
        
    def get_regex(self):
        if self._regex == _not_yet_inited:
            r = self.get_def_for('regex')
            if r: r = re.compile(r)
            self._regex = r
        return self._regex
                   
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
        if self._expected_types == _not_yet_inited:
            x = None
            if self.has_def_for('keys'): x = 'map'
            elif self.has_def_for(['max', 'min', 'xmax', 'xmin']): x = ['int', 'float', 'date']
            elif self.has_def_for('regex'): x = 'str'
            elif self.has_def_for('items'): x = 'seq'
            elif self.has_def_for('type'): x = self.node['type']
            elif self.has_def_for('default'): x = str(type(self.node['default']))
            elif self.has_def_for('fields'): x = 'tuple'
            elif self.has_def_for('multiple_of'): x = 'int'
            elif self.has_def_for('extras'): x = ['map', 'seq', 'tuple']
            # If we get here, there are 2 possible semantics that might still obtain:
            # 1. We're a degenerate schema with a single string that describes an expected data type.
            # 2. We are a very unconstrained schema where the data type isn't guessable or
            #    enforceable.
            elif is_string(self.node): x = self.node
            self._expected_types = x
        return self._expected_types
        
    def get_def_for(self, key):
        if self.has_def_for(key):
            try:
                return self.node[key]
            except:
                print(str(self.node))
                raise
        
    def validate(self, yaml_node, node_xpath='/'):
        '''
        Compare a node in a yaml doc/stream to a schema, and return a list of
        errors. An empty list means the yaml is valid according to the schema.
        '''
        errors = []
        # Convenience methods to unclutter code...
        ae = lambda msg: errors.append(schema_violation(self, node_xpath, msg, yaml_node))
        d = lambda key: self.get_def_for(key)
        expected = self.get_expected_types()
        actual = get_simple_type_name(yaml_node)
        has_type_error = False
        if (is_string(expected) and actual != expected) or (is_seq(expected) and actual not in expected):
            if is_seq(expected):
                expected = '/'.join(expected)
            ae('Expected node type to be %s, not %s.' % (expected, actual))
            has_type_error = True
        if not has_type_error:
            r = self.get_regex()
            if r and (not r.search(yaml_node)):
                ae('Value "%s" does not match regex /%s/.' % (yaml_node, r.pattern))
            n = d('multiple_of')
            if n and (yaml_node % n != 0):
                ae('Value is not a multiple of %d.' % n)
            n = d('max')
            if (n is not None) and (yaml_node > n):
                ae('Value is greater than max (%s)' % n)
            n = d('xmax')
            if (n is not None) and (yaml_node >= n):
                ae('Value is greater than or equal to xmax (%s)' % n)
            n = d('min')
            if (n is not None) and (yaml_node < n):
                ae('Value is less than min (%s)' % n)
            n = d('xmin')
            if (n is not None) and (yaml_node <= n):
                ae('Value is less than or equal to xmin (%s)' % n)
            
        
        return errors
