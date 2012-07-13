#!/usr/bin/env python

import sys

import sip
sip.setapi('QString', 2)

from PyQt4.QtGui import QApplication, QPlainTextEdit, QSyntaxHighlighter, \
    QTextCharFormat, QTextBlockUserData

from qutepart.SyntaxHighlighter import SyntaxHighlighter

text = \
"""mksv3 (12.06.3-1~ppa1) lucid; urgency=low

  * Added missing .ui and .json

 -- Andrei Kopats <hlamer@tut.by>  Mon, 18 Jun 2012 23:13:00 +0300
"""

text2 = \
"""<hlamer@tut.by>"""



if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    pte = QPlainTextEdit()
    pte.setPlainText(text2)
    hl = SyntaxHighlighter(pte.document())
    pte.show()
    app.exec_()
