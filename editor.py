#!/usr/bin/env python

import sys

if not '-p' in sys.argv:
    sys.path.insert(0, 'build/lib.linux-x86_64-2.6/')

import sip
sip.setapi('QString', 2)

from PyQt4.QtGui import QApplication


import qutepart


def main():
    args = [arg for arg in sys.argv \
                if not arg.startswith('-')]

    if len(args) != 2:
        print 'Usage:\n\t%s FILE' % sys.argv[0]

    filePath = args[1]
    
    with open(filePath) as file:
        text = unicode(file.read(), 'utf8')

    app = QApplication(sys.argv)
    
    qpart = qutepart.Qutepart()
    
    qpart.detectSyntax(sourceFilePath = filePath)
    
    qpart.setPlainText(text)
    
    qpart.setWindowTitle(filePath)
    
    qpart.resize(800, 600)
    qpart.show()
    
    from PyQt4.QtCore import QTimer
    if '-q' in sys.argv:
        QTimer.singleShot(0, app.quit)
    
    return app.exec_()
    

if __name__ == '__main__':
    main()
