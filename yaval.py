import os, sys, argparse, yaml, traceback, re

verbose = False

meta_schema = yaml.load(
'''
schema_id: b1dcd6d9-9680-4fb7-f569-616758d9b877
schema_name: yaval_schema
schema_version: 1.0

keys:
  type: !!str
  min_length: 1
  regex: /[-_a-zA-Z, 0-9]+/
  
schema_id:
  type: !!str
  regex: /[a-fA-F0-9]{8}-?([a-fA-F0-9]{4}-?){3}[a-fA-F0-9]{12}/
  
schema_version:
  type: !!str
  regex: /\d+(\.\d+){,3}(-[a-zA-Z+])/
''')

class validation_context:
    def __init__(self, path):
        self.path = path
        self.error_count = 0
        self.warning_count = 0

def yaval_one_node(schema, node, ctx):
    pass

def yaval_one_file(schema, doc_path, ctx):
    node = load_yaml(doc_path, ctx)
    if node:
        yaval_one_node(schema, node, ctx)

def report(msg, ctx):
    if verbose:
        sys.stdout.write(msg.strip() + '\n')
    
def err(msg, ctx, error=True):
    sys.stderr.write('Error: ' + msg.strip() + '\n')
    ctx.error_count += 1
            
def warn(msg, ctx):
    ctx.warning_count += 1
    if verbose:
        sys.stderr.write('Warning: ' + msg.strip() + '\n')
        
def capitalize(sentence):
    if sentence[0].islower():
        return sentence[0].upper() + sentence[1:]
    return sentence

def indent(paragraph, prefix):
    return prefix + paragraph.replace('\n', '\n' + prefix)
    
useless_yaml_ctx_pat = re.compile(r'\n\s*in "<string>",\s*', re.M)
def load_yaml(path, ctx):
    if os.path.isfile(path):
        report('Parsing yaml in %s.' % path, ctx)
        try:
            with open(path, 'r') as f:
                loaded = yaml.load(f.read())
                return loaded
        except yaml.YAMLError as e:
            e_txt = capitalize(useless_yaml_ctx_pat.sub(' ', str(e)))
            err('YAML syntax error in %s.\n%s' % (path, indent(e_txt, 2)), ctx)
        except:
            e_txt = traceback.format_exc()
            err('''YAML syntax error in %s.
  Location was not captured by parser; try simplifying doc bit
  by bit to narrow down the source.  
%s''' % (path, indent(traceback.format_exc(), '    ')), ctx)
    else:
        err('File %s does not exist or is unavailable.' % path, ctx)
    
def load_schema(schema_path, ctx):
    report('Loading schema from %s.' % schema_path, ctx)
    schema = load_yaml(schema_path, ctx)
    if schema:
        yaval_one_node(meta_schema, schema, ctx)
        if not ctx.error_count:
            return schema
    err("The schema itself is not valid, so it can't be used to test other docs.", ctx)

def yaval(schema_path, docs):
    # Begin by loading the schema and confirming that it's useful.
    exit_code = 0
    ctx = validation_context(schema_path)
    schema = load_schema(schema_path, ctx)
    if not schema:
        exit_code = 255
    else:
        # Now use the schema to validate each doc.
        for doc_path in docs:
            ctx = validation_context(doc_path)
            yaval_one_file(schema, doc_path, ctx)
            exit_code += ctx.error_count
    if not exit_code:
        print('Valid.')
    sys.exit(exit_code)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='yaval', description='Validate one or more yaml docs against a schema.')
    parser.add_argument('schema', help='schema to use')
    parser.add_argument('doc', nargs='+', help='doc(s) to validate')
    parser.add_argument('-v', '--verbose', help='display warnings and status', action='store_true')
    args = parser.parse_args()
    verbose = True #args.verbose
    yaval(args.schema, args.doc)