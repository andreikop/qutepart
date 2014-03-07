#!/usr/bin/env python

import os.path
import unittest
import sys


topLevelPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, topLevelPath)
sys.path.insert(0, os.path.join(topLevelPath, 'build/lib.linux-i686-2.7/'))
sys.path.insert(0, os.path.join(topLevelPath, 'build/lib.linux-x86_64-2.7/'))


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
