from datatypes import *

_no_value_provided = 'nO VaLuE PrOvIdEd'

class schema_violation:
    '''
    A validation_error is a single problem discovered during schema-based
    validation of a yaml doc.
    '''
    def __init__(self, schema_xpath, doc_xpath, msg, value=_no_value_provided):
        # Allow schema_xpath to be either a schema object or a string.
        if hasattr(schema_xpath, 'get_xpath'):
            schema_xpath = schema_xpath.get_xpath()
        self.schema_xpath = schema_xpath
        self.doc_xpath = doc_xpath
        self.msg = msg
        text = 'Doc:%s' % doc_xpath
        if value != _no_value_provided:
            if is_map(value):
                value = '{...}'
            elif is_seq(value):
                value = '[...]'
            text += ' with value=%s' % value
        self.text = text + ' violates %s. %s' % (schema_xpath, msg)
    def __str__(self):
        return self.text
