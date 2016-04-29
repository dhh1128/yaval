import os, sys, unittest

my_folder = os.path.dirname(os.path.abspath(__file__))
folder_under_test = os.path.abspath(os.path.join(my_folder, '..'))
sys.path = [folder_under_test] + sys.path

from schema import *

class schema_test(unittest.TestCase):

  def test_ctor(self):
      s = schema()

if __name__ == '__main__':
    unittest.main()