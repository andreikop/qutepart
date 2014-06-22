#!/usr/bin/env python3

import sys
import time

import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import QTimer, Qt
from PyQt4.QtGui import QApplication, QPlainTextEdit
from PyQt4.QtTest import QTest

import qutepart


app = QApplication(sys.argv)

q = qutepart.Qutepart()
q.detectSyntax(sourceFilePath=sys.argv[1])
print('Language:', q.language())

q.showMaximized()

with open(sys.argv[1]) as file_:
    text = file_.read()

clickTimes = {}

def click(key):
    clockBefore = time.clock()

    if isinstance(key, str):
        QTest.keyClicks(q, key)
    else:
        QTest.keyClick(q, key)
    while app.hasPendingEvents():
        app.processEvents()

    clockAfter = time.clock()
    ms = int((clockAfter - clockBefore) * 1000)
    clickTimes[ms] = clickTimes.get(ms, 0) + 1

def doTest():
    clockBefore = time.clock()
    for line in text.splitlines():
        indentWidth = len(line) - len(line.lstrip())
        while q.textCursor().positionInBlock() > indentWidth:
            click(Qt.Key_Backspace)
        for i in range(indentWidth - q.textCursor().positionInBlock()):
            click(Qt.Key_Space)

        line = line[indentWidth:]
        for char in line:
            click(char)
        click(Qt.Key_Enter)

    clockAfter = time.clock()
    typingTime = clockAfter - clockBefore
    print('Typed {} chars in {} sec. {} ms per character'.format(len(text), typingTime, typingTime * 1000 / len(text)))
    print('Time per click: count of clicks')
    clickTimeKeys = sorted(clickTimes.keys())
    for ckt in clickTimeKeys:
        print('       %5dms:            %4d' % (ckt, clickTimes[ckt]))

    app.quit()

QTimer.singleShot(0, doTest)
app.exec_()
