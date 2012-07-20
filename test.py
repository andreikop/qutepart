#!/usr/bin/env python

import sys

import sip
sip.setapi('QString', 2)

from PyQt4.QtGui import QApplication, QPlainTextEdit, QSyntaxHighlighter, \
    QTextCharFormat, QTextBlockUserData

from qutepart.SyntaxHighlighter import SyntaxHighlighter

text = """mksv3 (12.06.2-1~ppa1) lucid; urgency=low

  * Fix for Debian build system

 -- Andrei Kopats <hlamer@tut.by>  Mon, 18 Jun 2012 08:10:32 +0300
"""


text2 = \
"""mksv3 
 <hlamer@tut.by>"""



if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    pte = QPlainTextEdit()
    pte.setPlainText(text)
    hl = SyntaxHighlighter('debianchangelog.xml', pte.document())
    pte.show()
    app.exec_()
