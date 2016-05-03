import os, sys, unittest

my_folder = os.path.dirname(os.path.abspath(__file__))
folder_under_test = os.path.abspath(os.path.join(my_folder, '..'))
sys.path = [folder_under_test] + sys.path

from schema_violation import *

class schema_violation_test(unittest.TestCase):

  def test_ctor(self):
      sv = schema_violation('schema:top', 'loc', 'msg')
      self.assertEqual('schema:top', sv.schema_xpath)
      self.assertEqual('loc', sv.doc_xpath)
      self.assertEqual('msg', sv.msg)

  def test_str(self):
      sv = schema_violation('schema:top', 'loc', 'msg')
      self.assertEqual('Doc:loc violates schema:top. msg', str(sv))

if __name__ == '__main__':
    unittest.main()