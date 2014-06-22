#!/usr/bin/env python3

import unittest
import sys
import os.path

topLevelPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, topLevelPath)
sys.path.insert(0, os.path.join(topLevelPath, 'build/lib.linux-x86_64-2.6/'))
sys.path.insert(0, os.path.join(topLevelPath, 'build/lib.linux-x86_64-2.7/'))

from qutepart.syntax.parser import StringDetect, RegExpr

class TestCase(unittest.TestCase):
    def test_StringDetect(self):
        self.assertEqual(StringDetect._makeDynamicSubsctitutions('a%1c%3', ['a', '|']),
                         'a|c%3')

    def test_RegExp(self):
        self.assertEqual(RegExpr._makeDynamicSubsctitutions('a%1c%3', ['a', '|']),
                         'a\|c%3')


if __name__ == '__main__':
    unittest.main()
