#!/usr/bin/env python3

import unittest

import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..')))
from indenttest import IndentTest

class BaseTestClass(IndentTest):
    LANGUAGE = 'Scheme'
    INDENT_WIDTH = 2

class Test(BaseTestClass):
    def test_1(self):
        origin = [
            '(myfunc a'
            ]
        expected = [
            '(myfunc a',
            '        b'
            ]

        self.setOrigin(origin)
        self.setCursorPosition(0, 9);
        self.enter();
        self.type('b')
        self.verifyExpected(expected)

    def test_2(self):
        origin = [
            '(myfunc (if (a) a b)'
            ]
        expected = [
            '(myfunc (if (a) a b)',
            '        b'
            ]

        self.setOrigin(origin)
        self.setCursorPosition(0, 20);
        self.enter();
        self.type('b')
        self.verifyExpected(expected)

    def test_3(self):
        origin = [
            '(myfunc a)'
            ]
        expected = [
            '(myfunc a)',
            'b'
            ]

        self.setOrigin(origin)
        self.setCursorPosition(0, 10);
        self.enter();
        self.type('b')
        self.verifyExpected(expected)

    def test_4(self):
        origin = [
            '  (myfunc a)'
            ]
        expected = [
            '  (myfunc a)',
            '  b'
            ]

        self.setOrigin(origin)
        self.setCursorPosition(0, 12);
        self.enter();
        self.type('b')
        self.verifyExpected(expected)

    def test_5(self):
        origin = [
            '    (define'
            ]
        expected = [
            '    (define',
            '     b'
            ]

        self.setOrigin(origin)
        self.setCursorPosition(0, 11);
        self.enter();
        self.type('b')
        self.verifyExpected(expected)

    def test_6(self):
        origin = [
            'a',
            'b'
            ]
        expected = [
            'a',
            'b',
            'x'
            ]

        self.setOrigin(origin)
        self.setCursorPosition(1, 1);
        self.enter();
        self.type('x')
        self.verifyExpected(expected)

    def test_7(self):
        origin = [
            '   a',
            '']
        expected = [
            '   a',
            '',
            '   x'
            ]

        self.setOrigin(origin)
        self.setCursorPosition(1, 0);
        self.enter();
        self.tab();
        self.type('x')
        self.verifyExpected(expected)

    def test_8(self):
        origin = [
            '(define myfunc'
            ]
        expected = [
            '(define myfunc',
            '  x'
            ]

        self.setOrigin(origin)
        self.setCursorPosition(0, 14);
        self.enter();
        self.type('x')
        self.verifyExpected(expected)

    def test_9(self):
        origin = [
            '(let ((pi 3.14) (r 120))'
            ]
        expected = [
            '(let ((pi 3.14) (r 120))',
            '  x'
            ]

        self.setOrigin(origin)
        self.setCursorPosition(0, 24);
        self.enter();
        self.type('x')
        self.verifyExpected(expected)


class TestAutoindent(BaseTestClass):
    def test_1(self):
        origin = [
            '(define (fac n)',
            '(if (zero? n)',
            '1',
            '(* n (fac (- n 1)))))'
        ]
        expected = [
            '(define (fac n)',
            '  (if (zero? n)',
            '      1',
            '      (* n (fac (- n 1)))))'
        ]

        self.setOrigin(origin)
        self.alignAll()
        self.verifyExpected(expected)

    def test_2(self):
        origin = [
            '(let ((fnord 5)',
            '(answer 42))',
            '(frobnicate fnord answer))'
        ]
        expected = [
            '(let ((fnord 5)',
            '      (answer 42))',
            '  (frobnicate fnord answer))'
        ]

        self.setOrigin(origin)
        self.alignAll()
        self.verifyExpected(expected)

    def test_3(self):
        origin = [
            '(list (foo)',
            '(bar)',
            '(baz))'
        ]
        expected = [
            '(list (foo)',
            '      (bar)',
            '      (baz))'
        ]

        self.setOrigin(origin)
        self.alignAll()
        self.verifyExpected(expected)

    def test_4(self):
        origin = [
            '(list',
            '(foo)',
            '(bar)',
            '(baz))'
        ]
        expected = [
            '(list',
            ' (foo)',
            ' (bar)',
            ' (baz))'
        ]

        self.setOrigin(origin)
        self.alignAll()
        self.verifyExpected(expected)

    def test_5(self):
        origin = [
            '(let ((pi 3.14)',
            '(r 120))',
            '(* pi r r))'
        ]
        expected = [
            '(let ((pi 3.14)',
            '      (r 120))',
            '  (* pi r r))'
        ]

        self.setOrigin(origin)
        self.alignAll()
        self.verifyExpected(expected)

    def test_6(self):
        origin = [
        '(cond',
        '((good? x) (handle-good x))',
        '((bad? x)  (handle-bad x))',
        '((ugly? x) (handle-ugly x))',
        '(else      (handle-default x)))'
        ]
        expected = [
        '(cond',
        ' ((good? x) (handle-good x))',
        ' ((bad? x)  (handle-bad x))',
        ' ((ugly? x) (handle-ugly x))',
        ' (else      (handle-default x)))'
        ]

        self.setOrigin(origin)
        self.alignAll()
        self.verifyExpected(expected)

    def test_7(self):
        origin = [
            '(cond',
            '((good? x)',
            '(handle-good x))',
            '((bad? x)',
            '(handle-bad (if (really-bad? x)',
            '(really-bad->bad x)',
            'x)))',
            '((ugly? x)',
            '(handle-ugly x))',
            '(else',
            '(handle-default x)))'
        ]
        expected = [
            '(cond',
            ' ((good? x)',
            '  (handle-good x))',
            ' ((bad? x)',
            '  (handle-bad (if (really-bad? x)',
            '                  (really-bad->bad x)',
            '                  x)))',
            ' ((ugly? x)',
            '  (handle-ugly x))',
            ' (else',
            '  (handle-default x)))'
        ]

        self.setOrigin(origin)
        self.alignAll()
        self.verifyExpected(expected)

    def test_8(self):
        origin = [
            '(module gauss mzscheme',
            '',
            '(define (sum-up-to n)',
            '(/ (* n (+ n 1))',
            '2))',
            '',
            '(define (sum-up-to n)',
            '(/ (* n (+ n 1))',
            '2))',
            '',
            ')'
        ]
        expected = [
            '(module gauss mzscheme',
            '',
            '(define (sum-up-to n)',
            '  (/ (* n (+ n 1))',
            '     2))',
            '',
            '(define (sum-up-to n)',
            '  (/ (* n (+ n 1))',
            '     2))',
            '',
            ')'
        ]

        self.setOrigin(origin)
        self.alignAll()
        self.verifyExpected(expected)

if __name__ == '__main__':
    unittest.main()
