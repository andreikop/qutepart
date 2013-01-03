#!/usr/bin/env python

import sys

if not '-p' in sys.argv:
    sys.path.insert(0, 'build/lib.linux-x86_64-2.6/')

import sip
sip.setapi('QString', 2)

from PyQt4.QtGui import QApplication, QFont, QPlainTextEdit, QSyntaxHighlighter, \
    QTextCharFormat, QTextBlockUserData

from qutepart.syntax.highlighter import SyntaxHighlighter
from qutepart.syntax import SyntaxManager


def main():
    args = [arg for arg in sys.argv \
                if not arg.startswith('-')]

    if len(args) != 2:
        print 'Usage:\n\t%s FILE' % sys.argv[0]

    filePath = args[1]
    
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
    pte.resize(800, 600)
    pte.show()
    
    from PyQt4.QtCore import QTimer
    if '-q' in sys.argv:
        QTimer.singleShot(0, app.quit)
    return app.exec_()
    

if __name__ == '__main__':
    main()
