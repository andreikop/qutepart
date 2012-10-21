#!/usr/bin/env python

import unittest

import sys
sys.path.insert(0, '..')
from qutepart.Syntax import AbstractRule, RegExpr

class TestCase(unittest.TestCase):
    def test_AbstractRule(self):
        self.assertEqual(AbstractRule._makeDynamicStringSubsctitutions('a%2c%3', ['a', '|']),
                         'a|c%3')
    
    def test_RegExp(self):
        self.assertEqual(RegExpr._makeDynamicStringSubsctitutions('a%2c%3', ['a', '|']),
                         'a\|c%3')


if __name__ == '__main__':
    unittest.main()
