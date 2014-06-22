#!/usr/bin/env python3
# encoding: utf8


import os
import sys
import unittest

import base

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from qutepart import Qutepart




class Test(unittest.TestCase):
    """Base class for tests
    """
    app = base.papp  # app crashes, if created more than once

    def setUp(self):
        self.qpart = Qutepart()

    def tearDown(self):
        del self.qpart

    def _ws_test(self,
                 text,
                 expectedResult,
                 drawAny=[True, False],
                 drawIncorrect=[True, False],
                 useTab=[True, False],
                 indentWidth=[1, 2, 3, 4, 8]):
        for drawAnyVal in drawAny:
            self.qpart.drawAnyWhitespace = drawAnyVal

            for drawIncorrectVal in drawIncorrect:
                self.qpart.drawIncorrectIndentation = drawIncorrectVal

                for useTabVal in useTab:
                    self.qpart.indentUseTabs = useTabVal

                    for indentWidthVal in indentWidth:
                        self.qpart.indentWidth = indentWidthVal
                        try:
                            self._verify(text, expectedResult)
                        except:
                            print("Failed params:\n\tany {}\n\tincorrect {}\n\ttabs {}\n\twidth {}".format(
                                self.qpart.drawAnyWhitespace,
                                self.qpart.drawIncorrectIndentation,
                                self.qpart.indentUseTabs,
                                self.qpart.indentWidth))
                            raise

    def _verify(self, text, expectedResult):
        res = self.qpart._chooseVisibleWhitespace(text)
        for index, value in enumerate(expectedResult):
            if value == '1':
                if not res[index]:
                    self.fail("Item {} is not True:\n\t{}".format(index, res))
            elif value == '0':
                if res[index]:
                    self.fail("Item {} is not False:\n\t{}".format(index, res))
            else:
                assert value == ' '

    def test_1(self):
        # Trailing
        self._ws_test('   m xyz\t ',
                      '   0 00011',
                      drawIncorrect=[True])

    def test_2(self):
        # Tabs in space mode
        self._ws_test('\txyz\t',
                      '10001',
                      drawIncorrect=[True], useTab=[False])

    def test_3(self):
        # Spaces in tab mode
        self._ws_test(' 1  2   3     5',
                      '000001110111110',
                      drawIncorrect=[True], drawAny=[False], indentWidth=[3], useTab=[True])

    def test_4(self):
        # Draw any
        self._ws_test(' 1 1  2   3     5\t',
                      '100011011101111101',
                      drawAny=[True],
                      indentWidth=[2, 3, 4, 8])


if __name__ == '__main__':
    unittest.main()
