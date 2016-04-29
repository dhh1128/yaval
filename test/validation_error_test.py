import os, sys, unittest

my_folder = os.path.dirname(os.path.abspath(__file__))
folder_under_test = os.path.abspath(os.path.join(my_folder, '..'))
sys.path = [folder_under_test] + sys.path

from validation_error import *

class validation_error_test(unittest.TestCase):

  def test_ctor(self):
      ve = validation_error('ctx', 'loc', 'msg')
      self.assertEqual('ctx', ve.schema_ctx)
      self.assertEqual('loc', ve.location)
      self.assertEqual('msg', ve.msg)

  def test_str(self):
      ve = validation_error('ctx', 'loc', 'msg')
      self.assertEqual('Validation error raised by schema:ctx at loc. msg', str(ve))

if __name__ == '__main__':
    unittest.main()