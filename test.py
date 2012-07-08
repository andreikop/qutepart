#!/usr/bin/env python

import sys

import sip
sip.setapi('QString', 2)

from PyQt4.QtGui import QApplication, QPlainTextEdit, QSyntaxHighlighter, \
    QTextCharFormat, QTextBlockUserData

from qutepart.SyntaxHighlighter import SyntaxHighlighter

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    pte = QPlainTextEdit()
    pte.setPlainText("''\n")
    hl = SyntaxHighlighter(pte.document())
    pte.show()
    app.exec_()
