import os
import sys


import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtTest import QTest


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath('.'))

def in_main_loop(func, *args):
    """Decorator executes test method in the QApplication main loop.
    QAction shortcuts doesn't work, if main loop is not running.
    Do not use for tests, which doesn't use main loop, because it slows down execution.
    """
    def wrapper(*args):
        self = args[0]
        
        def execWithArgs():
            self.qpart.show()
            QTest.qWaitForWindowShown(self.qpart)
            while self.app.hasPendingEvents():
                self.app.processEvents()
            
            try:
                func(*args)
            finally:
                while self.app.hasPendingEvents():
                    self.app.processEvents()
                self.app.quit()
        
        QTimer.singleShot(0, execWithArgs)
        
        self.app.exec_()
    
    wrapper.__name__ = func.__name__  # for unittest test runner
    return wrapper
