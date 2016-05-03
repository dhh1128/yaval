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
        msg = 'Expected to see an error containing the text "%s".' % text
        if errors:
            msg += ' Instead, saw:\n  %s' % '\n  '.join([str(e) for e in errors])
        else:
            msg += ' Instead, no errors were reported.'
        raise Exception(msg)

def assert_valid(schema, *yaml_nodes):
    for yn_text in yaml_nodes:
        yaml_node = yaml.load(yn_text)
        errors = schema.validate(yaml_node, '/')
        if errors:
            msg = 'Expected to validate cleanly. Instead, saw:\n  %s' % '\n  '.join([str(e) for e in errors])
            raise Exception(msg)
 
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
      
    def test_yaval_schema_validates_itself(self):
        ys = get_yaval_schema()
        ys.validate(get_yaval_schema_yaml(), '/')
        
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