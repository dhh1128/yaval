float_type = type(1.0)
int_type = type(1)
string_type = type('')
date_type = 'iso8601'
unicode_type = type(u'')
bool_type = type(True)
map_type = type({})
seq_type = type([])
tuple_type = type(())

def is_string(obj):
    t = type(obj)
    return t is string_type or t is unicode_type

def is_int(obj):
    return type(obj) is int_type

def is_float(obj):
    return type(obj) is float_type

def is_number(obj):
    t = type(obj)
    return t is int_type or t is float_type

def is_map(obj):
    return type(obj) is map_type

def is_seq(obj):
    return type(obj) is seq_type

def is_tuple(obj):
    return type(obj) is tuple_type

def is_scalar(obj):
    t = type(obj)
    return not (t is map_type or t is seq_type or t is tuple_type)

def get_simple_type_name(obj):
    if is_string(obj):
        return 'str'
    if is_map(obj):
        return 'map'
    if is_seq(obj):
        return 'seq'
    if is_tuple(obj):
        return 'tuple'
    if is_int(obj):
        return 'int'
    if is_float(obj):
        return 'float'
    if is_bool(obj):
        return 'bool'
    if obj is None:
        return 'null'
    return str(type(obj))

