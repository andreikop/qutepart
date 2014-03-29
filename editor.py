#!/usr/bin/env python

import sys
import os
import logging
import argparse

import sip
sip.setapi('QString', 2)

from PyQt4.QtGui import QApplication, QMainWindow


def _parseCommandLine():
    parser = argparse.ArgumentParser(description='Qutepart test application')
    parser.add_argument('-b, --binary', action='store_true', dest='binary',
                        help='Use binary parser. Do ./setup.py build before using this flag')
    parser.add_argument('-d, --debug', action='store_true', dest='debug', help='Enable debug output')
    parser.add_argument('-q, --quit', action='store_true', dest='quit', help='Quit just after start')
    parser.add_argument('file', help='File to open')

    return parser.parse_args()

def _fixSysPath(binaryQutepart):
    executablePath = os.path.abspath(__file__)
    if executablePath.startswith('/home'):  # if executed from the sources
        qutepartDir = os.path.dirname(executablePath)
        sys.path.insert(0, qutepartDir) # do not import installed modules
        if binaryQutepart:
            sys.path.insert(0, qutepartDir + '/build/lib.linux-i686-2.7/')  # use built modules
            sys.path.insert(0, qutepartDir + '/build/lib.linux-x86_64-2.7/')  # use built modules





def main():
    ns = _parseCommandLine()
    _fixSysPath(ns.binary)

    import qutepart  # after correct sys.path has been set

    with open(ns.file) as file:
        text = unicode(file.read(), 'utf8')

    if ns.debug:
        logging.getLogger('qutepart').setLevel(logging.DEBUG)

    app = QApplication(sys.argv)

    window = QMainWindow()

    qpart = qutepart.Qutepart()
    window.setCentralWidget(qpart)

    firstLine = text.splitlines()[0] if text else None
    qpart.detectSyntax(sourceFilePath=ns.file, firstLine=firstLine)

    qpart.lineLengthEdge = 20

    qpart.drawIncorrectIndentation = True
    qpart.drawAnyWhitespace = False

    qpart.indentUseTabs = True

    qpart.text = text

    qpart.setWindowTitle(ns.file)

    menu = {'File':      ('printAction',),
            'Bookmarks': ('toggleBookmarkAction',
                          'nextBookmarkAction',
                          'prevBookmarkAction'),
            'Navigation':('scrollUpAction',
                          'scrollDownAction',
                          'selectAndScrollUpAction',
                          'selectAndScrollDownAction',
                          ),
            'Indentation':('increaseIndentAction',
                           'decreaseIndentAction',
                           'autoIndentLineAction',
                           'indentWithSpaceAction',
                           'unIndentWithSpaceAction'),
            'Lines':      ('moveLineUpAction',
                           'moveLineDownAction',
                           'deleteLineAction',
                           'copyLineAction',
                           'pasteLineAction',
                           'cutLineAction',
                           'duplicateLineAction'),
            'Edit'      : ('invokeCompletionAction',
                           'undoAction',
                           'redoAction'
                           )
    }
    for k, v in menu.items():
        menuObject = window.menuBar().addMenu(k)
        for actionName in v:
            menuObject.addAction(getattr(qpart, actionName))

    qpart.userWarning.connect(lambda text: window.statusBar().showMessage(text, 3000))

    window.resize(800, 600)
    window.show()

    from PyQt4.QtCore import QTimer
    if ns.quit:
        QTimer.singleShot(0, app.quit)

    return app.exec_()


if __name__ == '__main__':
    main()
