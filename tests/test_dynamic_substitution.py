#!/usr/bin/env python

import unittest

import sys
sys.path.insert(0, '..')
from qutepart.parser import StringDetect, RegExpr

class TestCase(unittest.TestCase):
    def test_StringDetect(self):
        self.assertEqual(StringDetect._makeDynamicStringSubsctitutions('a%2c%3', ['a', '|']),
                         'a|c%3')
    
    def test_RegExp(self):
        self.assertEqual(RegExpr._makeDynamicStringSubsctitutions('a%2c%3', ['a', '|']),
                         'a\|c%3')


if __name__ == '__main__':
    unittest.main()
