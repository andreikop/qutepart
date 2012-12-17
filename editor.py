#!/usr/bin/env python

import sys
sys.path.insert(0, 'build/lib.linux-x86_64-2.7/')

import sip
sip.setapi('QString', 2)

from PyQt4.QtGui import QApplication, QFont, QPlainTextEdit, QSyntaxHighlighter, \
    QTextCharFormat, QTextBlockUserData

from qutepart.SyntaxHighlighter import SyntaxHighlighter
from qutepart.syntax import SyntaxManager


def main():
    if len(sys.argv) != 2:
        print 'Usage:\n\t%s FILE' % sys.argv[0]

    filePath = sys.argv[1]
    
    try:
        syntax = SyntaxManager().getSyntaxBySourceFileName(filePath, SyntaxHighlighter.formatConverterFunction)
    except KeyError:
        print 'No syntax for', filePath
        return
    
    print 'Using syntax', syntax.name

    with open(filePath) as file:
        text = unicode(file.read(), 'utf8')

    app = QApplication(sys.argv)
    
    pte = QPlainTextEdit()
    pte.setPlainText(text)
    pte.setWindowTitle(filePath)
    pte.setFont(QFont("Monospace"))
    
    hl = SyntaxHighlighter(syntax, pte.document())
    pte.show()
    
    from PyQt4.QtCore import QTimer
    QTimer.singleShot(0, app.quit)
    return app.exec_()
    

if __name__ == '__main__':
    main()
