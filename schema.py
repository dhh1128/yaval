import re, weakref

_string_type = type('')
_unicode_type = type(u'')
def _is_string(obj):
    t = type(obj)
    return t == _string_type or t == _unicode_type


class schema:
    def __init__(self, name, node_from_schema_yaml, parent=None):
        self.name = name
        self.parent = None
        if parent:
            self.parent = weakref.ref(parent)
        else:
            self._node_root = node_from_schema_yaml            
        self.node = weakref.ref(node_from_schema_yaml)
        
    def get_xpath(self):
        if self.parent:
            return '%s/%s' % (self.parent().get_xpath(), self.name)
        else:
            return '/%s' % self.name
        
    def children(self):
        node = self.node()
        if not hasattr(node, 'children'):
            return
        contains = node['children']
        for key, value in contains.iteritems():
            yield schema(key, value, self)

    def extra_schemas(self):
        node = self.node()
        if not hasattr(node, 'contains'):
            return
        contains = node['contains']
        for key, value in contains.iteritems():
            yield schema(key, value, self)
