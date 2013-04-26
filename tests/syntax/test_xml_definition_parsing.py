#!/usr/bin/env python

import os
import unittest

import sys
sys.path.insert(0, '../..')
sys.path.insert(0, '.')
sys.path.insert(0, '../../build/lib.linux-x86_64-2.6/')

from qutepart.syntax import SyntaxManager

class XmlParsingTestCase(unittest.TestCase):
    def test_parse_all_definitions(self):
        """Parse all definitions
        Test, if we can open all xml files without exceptions.
        """
        xmlFilesPath = os.path.join(os.path.dirname(__file__), '..', '..', 'qutepart', 'syntax', 'data', 'xml')
        for xmlFileName in os.listdir(xmlFilesPath):
            if xmlFileName.endswith('.xml'):
                syntax = SyntaxManager().getSyntax(None, xmlFileName = xmlFileName)

if __name__ == '__main__':
    unittest.main()
