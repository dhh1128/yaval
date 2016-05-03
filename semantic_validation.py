import os

from validation_error import *

_float_type = type(1.0)
_int_type = type(1)
_string_type = type('')
_date_type = type(datetime.datetime)
_unicode_type = type(u'')
def is_string(obj):
    t = type(obj)
    return t == _string_type or t == _unicode_type

_map_type = type({})
def is_map(obj):
    return type(obj) == _map_type

_seq_type = type([])
def is_seq(obj):
    return type(obj) == _seq_type


schema_id_pat = re.compile(r'^(?i)[a-f0-9]{8}-?([a-f0-9]{4}-?){3}[a-f0-9]{12}$')
schema_version_pat = re.compile(r'^(?i)\d+(\.\d+){0,2}(-[-_a-z]+)?$')

_exactly_one_key_err_txt = 'Expected exactly one key (besides /schema_* and /patterns) to define the top-level node in the schema.'

def _append_reason(map, key, reason):
    if key not in map:
        map[key] = [reason]
    else:
        map[key].append(reason)
        
def _check_attrib_with_implied_types(node, implied_types, keys, types):
    assert type(keys) == _seq_type
    assert type(types) == _seq_type
    for key in keys:
        if key in node:
            for t in types:
                _append_reason(implied_keys, t, key)

def _get_implied_types_from_attribs(node):
    implied_types = {}
    _check_attrib_with_implied_type(node, implied_types, 'type', )
    if 'type' in node:
        implied_types[type(self.node['type'])] = ['type']
    if 'default' in node:
        implied_types[type(self.node['default'])] = ['default']
    _check_attrib_with_implied_types(node, implied_types, ['keys'], [_map_type])
    _check_attrib_with_implied_types(node, implied_types, ['items', 'fields'], [_seq_type])
    _check_attrib_with_implied_types(node, implied_types, ['regex'], [_string_type, _unicode_type])
    _check_attrib_with_implied_types(node, implied_types, ['max', 'min', 'xmax', 'xmin'], [_int_type, _float_type, _date_type])
    _check_attrib_with_implied_types(node, implied_types, ['multiple_of'], [_int_type])
    _check_attrib_with_implied_types(node, implied_types, ['extras'], [_map_type, _seq_type])
    return implied_types

def _check_mutually_exclusive(schema, node, props):
    mutually_exclusive = ['/' + k for k in props if k in node]
    if len(mutually_exclusive) > 1:
        raise validation_error(schema.get_xpath(), '/',
            'The %s properties are mutually exclusive.' % (' and '.join(mutually_exclusive)))

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
            return '/%s' % self.name
        
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
                    
    def _validate_type(self, yaml_node):
        
        _check_mutually_exclusive(self, yaml_node, ['keys', 'items', 'fields'])
        _check_mutually_exclusive(self, yaml_node, ['min', 'xmin'])
        _check_mutually_exclusive(self, yaml_node, ['max', 'xmax'])        
        it_map = _get_implied_types_from_attribs(yaml_node)
        if it_map and len(it_map) > 1:
            implied_types = it_map.keys()
            for it
            for t, keys_that_implied_t in it.iteritems():
                
            
            
