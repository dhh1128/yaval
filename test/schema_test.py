import os, sys, unittest, yaml

my_folder = os.path.dirname(os.path.abspath(__file__))
folder_under_test = os.path.abspath(os.path.join(my_folder, '..'))
yaval_schema_path = os.path.join(folder_under_test, 'yaval_schema.yaml')
sys.path = [folder_under_test] + sys.path

from schema import *

_ysy = None
def get_yaval_schema_yaml():
    global _ysy
    if _ysy is None:
        with open(yaval_schema_path, 'r') as f:
            doc = f.read()
            _ysy = yaml.load(doc)
    return _ysy
            

_ys = None
def get_yaval_schema():
    global _ys
    if _ys is None:
        _ys = schema('yaval', get_yaval_schema_yaml())
    return _ys


def assert_invalid(schema, text, *yaml_nodes):
    msgs = []
    for yn_text in yaml_nodes:
        yaml_node = yaml.load(yn_text)
        errors = schema.validate(yaml_node, '/')
        if errors:
            if not text: continue
            found = False
            for e in errors:
                if text in str(e):
                    found = True
                    break
            if found:
                continue
        if len(yn_text) < 100:
            msg = 'With value of %s, expected' % repr(yn_text)
        else:
            msg = 'Expected'
        msg += ' to see an error containing the text "%s".' % text
        if errors:
            msg += ' Instead, saw:\n  %s' % '\n  '.join([str(e) for e in errors])
        else:
            msg += ' Instead, no errors were reported.'
        msgs.append(msg)
    if msgs:
        raise Exception('\n'.join(msgs))

def assert_valid(schema, *yaml_nodes):
    msgs = []
    for yn_text in yaml_nodes:
        yaml_node = yaml.load(yn_text)
        errors = schema.validate(yaml_node, '/')
        if errors:
            msg = 'Expected to validate cleanly. Instead, saw:\n  %s' % '\n  '.join([str(e) for e in errors])
            msgs.append(msg)
    if msgs:
        raise Exception('\n'.join(msgs))
        
def assert_expected_types(schema_txt, expected_types):
    if is_string(expected_types):
        expected_types = expected_types.split(',')
        expected_types = sorted(expected_types)
    expected_types = str(expected_types)
    s = schema('x', yaml.load(schema_txt))
    actual_types = s.get_expected_types()
    if actual_types is None:
        actual_types = 'None'
    else:
        actual_types = str(sorted(actual_types))
    if actual_types != expected_types:
        msg = 'Expected schema of %s to report expected types = %s, but got %s instead.' % (
            str(s.node), expected_types, actual_types)
        raise Exception(msg)
    #print('Schema of %s correctly reported expected types = %s.' % (str(s.node), expected_types))        
        
 
class schema_test(unittest.TestCase):
    
    def test_xpath1(self):
        s = schema('any_string', yaml.load('str'))
        self.assertEquals('schema:any_string', s.get_xpath())

    def test_ultra_simple(self):
        s = schema('any_string', yaml.load('str'))
        assert_valid(s, 'hello', '"hi"', 'this is a test', '\nthis is a test\nparagraph')
        assert_invalid(s, 'Expected node type to be str', '456789', '{}', '[]', '3.14')
        s = schema('any_int', yaml.load('int'))
        assert_valid(s, '123')
        assert_invalid(s, 'Expected node type to be int', 'hello', '{}', '[]', '3.14')
        
    def test_min_out_of_range(self):
        s = schema('min_25', yaml.load('min: 25'))
        assert_valid(s, '25', '30', '!!float 3.2e7')
        assert_invalid(s, 'less than', '24', '-3', '0', '!!float -3.2e7', '!!float 3.2e-7')
        assert_invalid(s, 'node type', 'hello')
        
    def test_min_0(self):
        s = schema('min_0', yaml.load('min: 0'))
        assert_invalid(s, 'less than', '-1')
        assert_invalid(s, 'Expected node type to be', 'hello', '', '[]', '{}')
        
    def test_min_0dot0(self):
        s = schema('min_0dot0', yaml.load('min: 0.0'))
        assert_invalid(s, 'less than', '-1')
        assert_invalid(s, 'Expected node type to be', 'hello', '', '[]', '{}')
        
    def test_xmin_out_of_range(self):
        s = schema('xmin_25', yaml.load('xmin: 25'))
        assert_valid(s, '26', '30', '!!float 3.2e7')
        assert_invalid(s, 'less than or equal to', '25', '25.0', '-3', '0', '!!float -3.2e7', '!!float 3.2e-7')
        assert_invalid(s, 'Expected node type to be', 'hello', '', '[]', '{}')
        
    def test_xmin_0(self):
        s = schema('xmin_0', yaml.load('xmin: 0'))
        assert_invalid(s, 'less than or equal to', '0')
        assert_invalid(s, 'Expected node type to be', 'hello', '', '[]', '{}')        
        
    def test_max_out_of_range(self):
        s = schema('max_25', yaml.load('max: 25'))
        assert_valid(s, '2', '10', '3.14', '0', '-3', '!!float 3.2e-7')
        assert_invalid(s, 'greater than', '34', '!!float 3.2e7')
        assert_invalid(s, 'Expected node type to be', 'hello', '', '[]', '{}')
        
    def test_max_0(self):
        s = schema('max_0', yaml.load('max: 0'))
        assert_invalid(s, 'greater than', '1')
        assert_invalid(s, 'Expected node type to be', 'hello', '', '[]', '{}')
      
    def test_xmax_out_of_range(self):
        s = schema('xmax_25', yaml.load('xmax: 25'))
        assert_valid(s, '2', '10', '3.14', '0', '-3', '!!float 3.2e-7')
        assert_invalid(s, 'greater than or equal to', '25', '25.0', '34', '!!float 3.2e7')
        assert_invalid(s, 'Expected node type to be', 'hello', '', '[]', '{}')
      
    def test_xmax_0(self):
        s = schema('xmax_0', yaml.load('xmax: 0'))
        assert_invalid(s, 'greater than or equal to', '0')
        assert_invalid(s, 'Expected node type to be', 'hello', '', '[]', '{}')
        
    def test_multiple_of(self):
        s = schema('mult3', yaml.load('multiple_of: 3'))
        assert_valid(s, '3', '6', '7611849', '0', '-3')
        assert_invalid(s, 'not a multiple of', '5', '2', '-26')
        assert_invalid(s, 'Expected node type to be int', '3.14', '27.0', 'hello', '{}', '[]', '')
        
    def test_length_constraints(self):
        s = schema('3to5', yaml.load('min_length: 3\nmax_length: 5'))
        assert_valid(s, 'abc', 'abcde', 'four', '[a, b, c]', '[a, b, c, d, e]', '{a: 1, b: 2, c: 3}', '{a: 1, b: 2, c: 3, d: 4, e: 5}')
        assert_invalid(s, 'greater than max_length', 'too big', 'way, way too big', 'sixsix', '[1,2,3,4,5,6]', '{a: 1, b: 2, c: 3, d: 4, e: 5, f: 6}')
        assert_invalid(s, 'less than min_length', 'hi', '[]', '{x: 1}')
        assert_invalid(s, 'Expected node type to be', '')
        
    def test_expected_types(self):
        assert_expected_types('min_length: 1\nmax_length: 2', 'str,seq,map,tuple')
        assert_expected_types('min_length: 1\nmultiple_of: 2', [])
        assert_expected_types('min_length: 1\nregex: x', ['str'])
        assert_expected_types('max_length: 1\nitems: x', ['seq'])
        assert_expected_types('multiple_of: 1\nregex: x', [])
        
    def test_yaval_schema_validates_itself(self):
        ys = get_yaval_schema()
        ys.self_validate()
        
    def test_yaval_schema_requires_map_at_root(self):
        return
        ys = get_yaval_schema()
        assert_invalid(ys, 'hello', 'must be a map')
        assert_invalid(ys, '25', 'must be a map')
        assert_invalid(ys, '[]', 'must be a map')
        
    def test_yaval_schema_allows_exactly_one_extra_key(self):
        return
        ys = get_yaval_schema()
        #import pdb
        #pdb.set_trace()
        assert_invalid(ys, 'x: 0\ny: 1', 'exactly one key')


if __name__ == '__main__':
    unittest.main()