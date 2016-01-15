import os
import sys
import time

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QKeySequence
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath('.'))

# Create a single, persistent QApplication for use in all tests.
papp = QApplication(sys.argv)


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
            QTest.qWaitForWindowExposed(self.qpart)
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

def keySequenceClicks(widget, keySequence, extraModifiers=Qt.NoModifier):
    """Use QTest.keyClick to send a QKeySequence to a widget."""

    # This is based on a simplified version of http://stackoverflow.com/questions/14034209/convert-string-representation-of-keycode-to-qtkey-or-any-int-and-back. I added code to handle the case in which the resulting key contains a modifier (for example, Shift+Home). When I execute QTest.keyClick(widget, keyWithModifier), I get the error "ASSERT: "false" in file .\qasciikey.cpp, line 495". To fix this, the following code splits the key into a key and its modifier.
    # Bitmask for all modifier keys.
    modifierMask = int(Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier |
                       Qt.MetaModifier |  Qt.KeypadModifier)
    ks = QKeySequence(keySequence)
    # For now, we don't handle a QKeySequence("Ctrl") or any other modified by itself.
    assert ks.count() > 0
    for _, key in enumerate(ks):
        modifiers = Qt.KeyboardModifiers((key & modifierMask) | extraModifiers)
        key = key & ~modifierMask
        QTest.keyClick(widget, key, modifiers)


