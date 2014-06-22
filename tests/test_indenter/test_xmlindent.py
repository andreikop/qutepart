#!/usr/bin/env python3

import unittest

import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..')))
from indenttest import IndentTest

class BaseTestClass(IndentTest):
    LANGUAGE = 'XML'
    INDENT_WIDTH = 2

class Split(BaseTestClass):
    def test_split1(self):
        origin = [
            '<one><two>',
            '']
        expected = [
            '<one>',
            '  <two>',
            '']

        self.setOrigin(origin)

        self.alignLine(0)
        self.verifyExpected(expected)

    def test_split2(self):
        origin = [
            '<one><two> text </two></one>',
            '']
        expected = [
            '<one>',
            '  <two> text </two>',
            '</one>',
            '']

        self.setOrigin(origin)

        self.alignLine(0)
        self.verifyExpected(expected)

    def test_split3(self):
        origin = [
            '<property name="geometry">',
            '<rect>',
            '<x>0</x><y>0</y><width>421</width><height>300</height>',
            '</rect>',
            '</property>'
        ]
        expected = [
            '<property name="geometry">',
            '  <rect>',
            '    <x>0</x>',
            '    <y>0</y>',
            '    <width>421</width>',
            '    <height>300</height>',
            '  </rect>',
            '</property>'
        ]

        self.setOrigin(origin)
        for i in range(8):
            self.alignLine(i)
        self.verifyExpected(expected)

    def test_split4(self):
        origin = [
            '<a><b>8</b></a>'
        ]
        expected = [
            '<a>',
            '  <b>8</b>',
            '</a>']

        self.setOrigin(origin)

        self.alignLine(0)
        self.verifyExpected(expected)

class Align(BaseTestClass):
    def test_align1(self):
        origin = [
            '<one>',
            '<two>'
        ]
        expected = [
            '<one>',
            '  <two>'
        ]

        self.setOrigin(origin)

        self.alignLine(1)
        self.verifyExpected(expected)

    def test_align2(self):
        origin = [
            '    text',
            '    </two>'
        ]
        expected = [
            '    text',
            '  </two>'
        ]

        self.setOrigin(origin)

        self.alignLine(1)
        self.verifyExpected(expected)

    def test_align3(self):
        origin = [
            '  <!-- blabla -->',
            '      <tag>']
        expected = [
            '  <!-- blabla -->',
            '  <tag>']

        self.setOrigin(origin)

        self.alignLine(1)
        self.verifyExpected(expected)

    def test_align4(self):
        origin = [
            '<?xml version="1.0" encoding="UTF-8"?>'
        ]
        expected = [
            '<?xml version="1.0" encoding="UTF-8"?>'
        ]

        self.setOrigin(origin)

        self.alignLine(0)
        self.verifyExpected(expected)

    def test_align5(self):
        origin = [
            '<a>',
            '<b>'
        ]
        expected = [
            '<a>',
            '  <b>'
        ]

        self.setOrigin(origin)

        self.alignLine(1)
        self.verifyExpected(expected)


class Slash(BaseTestClass):
    def test_slash1(self):
        origin = [
            '    text',
            '    <',
            '']
        expected = [
            '    text',
            '  </',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.type('/')
        self.verifyExpected(expected)

    def test_slash2(self):
        """Do not indent, if in text block
        """
        origin = [
            '    text',
            '    <tag text="',
            '']
        expected = [
            '    text',
            '    <tag text="/',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(1, 15);
        self.type('/')
        self.verifyExpected(expected)

    def test_slash3(self):
        """Do not indent, if previous line opens tag
        """
        origin = [
            '    <tag>',
            '    <',
            '']
        expected = [
            '    <tag>',
            '    </',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(1, 5);
        self.type('/')
        self.verifyExpected(expected)

    def test_slash4(self):
        origin = [
            '    text',
            '    <blabla',
            '']
        expected = [
            '    text',
            '    </blabla',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.type('/')
        self.verifyExpected(expected)



class Greater(BaseTestClass):
    def test_greater1(self):
        """closing tag, decrease indentation when previous didn't open a tag
        """
        origin = [
            '    text',
            '    </tag',
            '']
        expected = [
            '    text',
            '  </tag>',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(1, 9);
        self.type('>')
        self.verifyExpected(expected)

    def test_grater2(self):
        """keep indent when prev line opened a tag
        """
        origin = [
            '    <tag>',
            '    </tag',
            '']
        expected = [
            '    <tag>',
            '    </tag>',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(1, 9);
        self.type('>')
        self.verifyExpected(expected)

    def test_greater3(self):
        """zero indent for <?xml
        """
        origin = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<tag',
            '']
        expected = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<tag>',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(1, 4);
        self.type('>')
        self.verifyExpected(expected)

    def test_greater4(self):
        """zero indent for <!DOCTYPE
        """
        origin = [
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd>',
            '<tag',
            '']
        expected = [
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd>',
            '<tag>',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(1, 4);
        self.type('>')
        self.verifyExpected(expected)

    def test_greater5(self):
        """ keep indent when prev line closed a tag or was a comment
        """
        origin = [
            '  <!-- blabla -->',
            '  <tag',
            '']
        expected = [
            '  <!-- blabla -->',
            '  <tag>',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(1, 6);
        self.type('>')
        self.verifyExpected(expected)

    def test_greater6(self):
        """ keep indent when prev line closed a tag or was a comment
        """
        origin = [
            '  </tag>',
            '  <tag',
            '']
        expected = [
            '  </tag>',
            '  <tag>',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(1, 6);
        self.type('>')
        self.verifyExpected(expected)

    def test_greater7(self):
        """ increase indent
        """
        origin = [
            '  <tag>',
            '  <othertag',
            '']
        expected = [
            '  <tag>',
            '    <othertag>',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(1, 11);
        self.type('>')
        self.verifyExpected(expected)

class Enter(BaseTestClass):
    def test_enter1(self):
        """zero indent for <?xml
        """
        origin = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '']
        expected = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(0, 38);
        self.enter()
        self.verifyExpected(expected)

    def test_enter2(self):
        """zero indent for <!DOCTYPE
        """
        origin = [
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd>',
            '']
        expected = [
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd>',
            '',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(1, 93);
        self.enter()
        self.verifyExpected(expected)

    def test_enter3(self):
        """ keep indent when prev line was a comment
        """
        origin = [
            '  <!-- blabla -->',
            '']
        expected = [
            '  <!-- blabla -->',
            '  ',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(0, 17);
        self.enter()
        self.verifyExpected(expected)

    def test_enter4(self):
        """ keep indent when prev line closed a tag
        """
        origin = [
            '  </tag>',
            '']
        expected = [
            '  </tag>',
            '  ',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(0, 8);
        self.enter()
        self.verifyExpected(expected)

    def test_enter5(self):
        """increase indent when prev line opened a tag
        """
        origin = [
            '  <tag>',
            '']
        expected = [
            '  <tag>',
            '    ',
            '']

        self.setOrigin(origin)

        self.setCursorPosition(0, 7);
        self.enter()
        self.verifyExpected(expected)


if __name__ == '__main__':
    unittest.main()
