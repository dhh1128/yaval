import os, re, yaml

from schema_violation import *
from datatypes import *

schema_id_pat = re.compile(r'^(?i)[a-f0-9]{8}-?([a-f0-9]{4}-?){3}[a-f0-9]{12}$')
schema_version_pat = re.compile(r'^(?i)\d+(\.\d+){0,2}(-[-_a-z]+)?$')
yaval_schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'yaval_schema.yaml')

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
        self._impled_type_map = None
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
        '''
        Does this schema have a definition for any key in a certain list?
        If so, return those keys that are defined. Otherwise, return empty
        list.
        '''
        if not is_map(self.node): return []
        if is_string(keys):
            keys = [keys]
        return [k for k in keys if k in self.node]
        
    def get_regex(self):
        if self._regex == _not_yet_inited:
            r = self.get_def_for('regex')
            if r: r = re.compile(r)
            self._regex = r
        return self._regex
                   
    def get_expected_types(self):
        '''
        Return a list of the type names that this schema expects/accepts.
        Normally list will contain a single string like 'str' or 'map'.
        However, it may contain the name of another schema node (e.g., 'email'
        might refer to a node in the schema that defines email addresses), or
        it may be an empty list if no datatypes are compatible with the set
        of properties in the schema; this would indicate a bad schema. In such
        cases, self._impled_type_map will contain diagnostic info. The function
        may also return None if the schema imposes no constraints on the type
        of the yaml node it validates.
        '''
        if self._expected_types == _not_yet_inited:
            # The common case at leaf nodes is a simple declaration of datatype.
            # No further analysis is needed for this case.
            if is_string(self.node):
                self._expected_types = [self.node]
            else:
                # First, figure out which types are implied by which properties.
                # There are faster ways to narrow down to a single type, but this
                # way provides the most helpful diagnostics for schema writers.
                x = {}
                # We need some helper functions that know about our local variables.
                # We could use lambdas, but assignment gets tricky in them. This
                # syntax is clear and is still lambda-like.
                def mark_types_for_key(key, types):
                    x[key] = types
                def check_for(keys, types):
                    for k in self.has_def_for(keys): mark_types_for_key(k, types)
                check_for('keys', ['map'])
                check_for('regex', ['str'])
                check_for('items', ['seq'])
                check_for('fields', ['tuple'])
                check_for('multiple_of', ['int'])
                if self.has_def_for('type'):
                    x['type'] = [self.node['type']]
                if self.has_def_for('default'):
                    x['default'] = [get_simple_type_name(self.node['default'])]
                check_for(['max', 'min', 'xmax', 'xmin'], ['int', 'float', 'date'])
                check_for(['min_length', 'max_length'], ['str', 'seq', 'map', 'tuple'])
                check_for('extras', ['map', 'seq', 'tuple'])
                self._impled_type_map = x
                if not x:
                    self._expected_types = None
                else:
                    keys = x.keys()
                    intersect = x[keys[0]]
                    for i in xrange(1,len(keys)):
                        intersect = [k for k in intersect if k in x[keys[i]]]
                    self._expected_types = sorted(intersect) # sort for consistency
        return self._expected_types
        
    def get_def_for(self, key):
        if self.has_def_for(key):
            try:
                return self.node[key]
            except:
                print(str(self.node))
                raise
            
    def self_validate(self):
        with open(yaval_schema_path, 'r') as f:
            yaval_schema = yaml.load(f.read())
        self.validate(yaval_schema, self.node)
        
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
        if expected is None:
            pass
        elif not expected:
            ae('No datatype permits all the properties')
        elif actual not in expected:
            expected = '|'.join(expected)
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
                ae('Value is greater than max (%s).' % n)
            n = d('xmax')
            if (n is not None) and (yaml_node >= n):
                ae('Value is greater than or equal to xmax (%s).' % n)
            n = d('min')
            if (n is not None) and (yaml_node < n):
                ae('Value is less than min (%s)' % n)
            n = d('xmin')
            if (n is not None) and (yaml_node <= n):
                ae('Value is less than or equal to xmin (%s).' % n)
            n = d('max_length')
            if (n is not None) and (len(yaml_node) > n):
                ae('Length of %d is greater than max_length (%s).' % (len(yaml_node), n))
            n = d('min_length')
            if (n is not None) and (len(yaml_node) < n):
                ae('Length of %d is less than min_length (%s).' % (len(yaml_node), n))
        return errors
