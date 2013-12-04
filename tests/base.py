import os
import sys
import unittest
import time


import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtTest import QTest


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath('.'))

def _processPendingEvents(app):
    """Process pending application events.
    Timeout is used, because on Windows hasPendingEvents() always returns True
    """
    t = time.time()
    while app.hasPendingEvents() and (time.time() - t < 0.1):
        app.processEvents()


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
            _processPendingEvents(self.app)
            
            try:
                func(*args)
            finally:
                _processPendingEvents(self.app)
                self.app.quit()
        
        QTimer.singleShot(0, execWithArgs)
        
        self.app.exec_()
    
    wrapper.__name__ = func.__name__  # for unittest test runner
    return wrapper


class Runner(unittest.TextTestRunner):
    """Test runner executes tests in forked processes.
    It is necessary, because Qt crashes, if QApplication
    has been created and executed several times in 1 process
    
    Runner doesn't produce output, absolutelly equal to standard class,
    but results are printed to the console, and it works quite good
    """
    def _run_suite(self, result, suite):
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                self._run_suite(result, item)
            else:
                self._run_test(result, item)
        
    def _run_test(self, result, test):
        if os.fork():
            # main process
            pid, code = os.wait()
            if code != 0:
                result.failures.append((test, 'Returned != 0 code'))
                result.printErrors()
        else:
            # child process
            test(result)
            
            if result.wasSuccessful():
                sys.exit(0)
            else:
                result.printErrors()
                sys.exit(1)
    
    def run(self, suite):
        result = self._makeResult()
        self._run_suite(result, suite)
        print
        return result


def main():
    unittest.main(testRunner=Runner)
