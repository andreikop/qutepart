#!/usr/bin/env python

import sys
import os
import logging


executablePath = os.path.abspath(__file__)
if executablePath.startswith('/home'):  # if executed from the sources
    sys.path.insert(0, os.path.dirname(executablePath)) # do not import installed modules
    if not '-p' in sys.argv:
        sys.path.insert(0, '/home/a/code/qutepart/build/lib.linux-i686-2.7/')  # use built modules
        sys.path.insert(0, '/home/a/code/qutepart/build/lib.linux-x86_64-2.7/')  # use built modules



import sip
sip.setapi('QString', 2)

from PyQt4.QtGui import QApplication, QMainWindow


import qutepart


def main():
    args = [arg for arg in sys.argv \
                if not arg.startswith('-')]

    if len(args) != 2:
        print 'Usage:\n\t%s FILE' % sys.argv[0]

    filePath = args[1]
    
    with open(filePath) as file:
        text = unicode(file.read(), 'utf8')

    if '-d' in sys.argv:
        logging.getLogger('qutepart').setLevel(logging.DEBUG)
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()

    qpart = qutepart.Qutepart()
    window.setCentralWidget(qpart)
    
    line = None
    with open(filePath) as f:
        line = f.readline()
    
    qpart.detectSyntax(sourceFilePath = filePath, firstLine=line)
    
    qpart.text = text
    
    qpart.setWindowTitle(filePath)
    
    menu = {'Bookmarks': ('toggleBookmarkAction',
                          'nextBookmarkAction',
                          'prevBookmarkAction'),
            'Navigation':('scrollUpAction',
                          'scrollDownAction',
                          'selectAndScrollUpAction',
                          'selectAndScrollDownAction',
                          ),
            'Edit'      : ('decreaseIndentAction',
                           'autoIndentLineAction',
                           'moveLineUpAction',
                           'moveLineDownAction',
                           'deleteLineAction',
                           'copyLineAction',
                           'pasteLineAction',
                           'cutLineAction',
                           'duplicateLineAction',
                           )
    }
    for k, v in menu.items():
        menuObject = window.menuBar().addMenu(k)
        for actionName in v:
            menuObject.addAction(getattr(qpart, actionName))
    
    window.resize(800, 600)
    window.show()
    
    from PyQt4.QtCore import QTimer
    if '-q' in sys.argv:
        QTimer.singleShot(0, app.quit)
    
    return app.exec_()
    

if __name__ == '__main__':
    main()
