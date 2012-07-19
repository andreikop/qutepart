#!/usr/bin/env python

import sys

import sip
sip.setapi('QString', 2)

from PyQt4.QtGui import QApplication, QPlainTextEdit, QSyntaxHighlighter, \
    QTextCharFormat, QTextBlockUserData

from qutepart.SyntaxHighlighter import SyntaxHighlighter

text = """Source: mksv3
Section: editors
Priority: optional
Maintainer: Andrei Kopats <hlamer@tut.by>
Build-Depends: debhelper (>= 7.4.1), python-support, python (>= 2.6)
Standards-Version: 3.9.2
Homepage: https://github.com/hlamer/mksv3
Vcs-Git: https://github.com/hlamer/mksv3
Vcs-Browser: https://github.com/hlamer/mksv3

Package: mksv3
Architecture: all
Depends: ${misc:Depends}, ${python:Depends}, python-qt4, python-qscintilla2, python-pyparsing
Suggests: python-pygments, mit-scheme, python-markdown
Description: Simple programmers text editor
 Some of features:
  * Syntax highlighting for more than 30 languages
  * Bookmarks
  * Search and replace functionality for files and directories. Regexps are supported.
  * File browser
  * Autocompletion, based on document contents
  * Hightly configurable
  * MIT Scheme REPL integration
"""


text2 = \
""" ${a} ${b}"""



if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    pte = QPlainTextEdit()
    pte.setPlainText(text2)
    hl = SyntaxHighlighter('debiancontrol.xml', pte.document())
    pte.show()
    app.exec_()
