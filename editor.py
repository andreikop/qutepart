#!/usr/bin/env python

import sys

import sip
sip.setapi('QString', 2)

from PyQt4.QtGui import QApplication, QFont, QPlainTextEdit, QSyntaxHighlighter, \
    QTextCharFormat, QTextBlockUserData

from qutepart.SyntaxHighlighter import SyntaxHighlighter
from qutepart.syntax_manager import SyntaxManager


def main():
    if len(sys.argv) != 2:
        print 'Usage:\n\t%s FILE' % sys.argv[0]

    filePath = sys.argv[1]
    
    try:
        syntax = SyntaxManager().getSyntaxBySourceFileName(filePath)
    except KeyError:
        print 'No syntax for', filePath
        return
    
    print 'Using syntax', syntax.name

    with open(filePath) as file:
        text = file.read()

    app = QApplication(sys.argv)
    
    pte = QPlainTextEdit()
    pte.setPlainText(text)
    pte.setWindowTitle(filePath)
    pte.setFont(QFont("Monospace"))
    
    hl = SyntaxHighlighter(syntax, pte.document())
    pte.show()
    
    from PyQt4.QtCore import QTimer
    #QTimer.singleShot(0, app.quit)
    return app.exec_()
    

if __name__ == '__main__':
    main()
