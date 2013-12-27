"""Line numbers and bookmarks areas
"""

from PyQt4.QtCore import QPoint, Qt, pyqtSignal
from PyQt4.QtGui import QPainter, QPalette, \
                        QPixmap, \
                        QTextBlock, QWidget

import qutepart
from qutepart.bookmarks import Bookmarks


class LineNumberArea(QWidget):
    """Line number area widget
    """
    _LEFT_MARGIN = 5
    _RIGHT_MARGIN = 3

    def __init__(self, qpart):
        QWidget.__init__(self, qpart)
        self._qpart = qpart

    def sizeHint(self, ):
        """QWidget.sizeHint() implementation
        """
        return QSize(self.width(), 0)

    def paintEvent(self, event):
        """QWidget.paintEvent() implementation
        """
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.palette().color(QPalette.Window))
        painter.setPen(Qt.black)

        block = self._qpart.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self._qpart.blockBoundingGeometry(block).translated(self._qpart.contentOffset()).top())
        bottom = top + int(self._qpart.blockBoundingRect(block).height())
        singleBlockHeight = self._qpart.cursorRect().height()

        width = None
        wrapMarkerColor = None

        boundingRect = self._qpart.blockBoundingRect(block)
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.drawText(0, top, self.width() - self._RIGHT_MARGIN, self._qpart.fontMetrics().height(),
                                 Qt.AlignRight, number)
                if boundingRect.height() >= singleBlockHeight * 2:  # wrapped block
                    if width is None:
                        width = self.width()  # laizy calculation
                    painter.fillRect(1, top + singleBlockHeight,
                                     width - 2, boundingRect.height() - singleBlockHeight - 2,
                                     Qt.darkGreen)

            block = block.next()
            boundingRect = self._qpart.blockBoundingRect(block)
            top = bottom
            bottom = top + int(boundingRect.height())
            blockNumber += 1

    def width(self):
        """Desired width. Includes text and margins
        """
        digits = len(str(max(1, self._qpart.blockCount())))
        return self._LEFT_MARGIN + self._qpart.fontMetrics().width('9') * digits + self._RIGHT_MARGIN


class MarkArea(QWidget):

    blockClicked = pyqtSignal(QTextBlock)

    _MARGIN = 1

    def __init__(self, qpart):
        QWidget.__init__(self, qpart)
        self._qpart = qpart

        qpart.blockCountChanged.connect(self.update)

        defaultSizePixmap = QPixmap(qutepart.getIconPath('bookmark.png'))
        iconSize = self._qpart.cursorRect().height()
        self._bookmarkPixmap = defaultSizePixmap.scaled(iconSize, iconSize)

    def sizeHint(self, ):
        """QWidget.sizeHint() implementation
        """
        return QSize(self.width(), 0)

    def paintEvent(self, event):
        """QWidget.paintEvent() implementation
        Draw markers
        """
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.palette().color(QPalette.Window))

        block = self._qpart.firstVisibleBlock()
        blockBoundingGeometry = self._qpart.blockBoundingGeometry(block).translated(self._qpart.contentOffset())
        top = blockBoundingGeometry.top()
        bottom = top + blockBoundingGeometry.height()

        for block in qutepart.iterateBlocksFrom(block):
            if top > event.rect().bottom():
                break
            if block.isVisible() and \
               bottom >= event.rect().top() and \
               Bookmarks.isBlockMarked(block):
                painter.drawPixmap(0, top, self._bookmarkPixmap)

            top += self._qpart.blockBoundingGeometry(block).height()

    def width(self):
        """Desired width. Includes text and margins
        """
        return self._MARGIN + self._bookmarkPixmap.width() + self._MARGIN

    def mousePressEvent(self, mouseEvent):
        cursor = self._qpart.cursorForPosition(QPoint(0, mouseEvent.y()))
        block = cursor.block()
        blockRect = self._qpart.blockBoundingGeometry(block).translated(self._qpart.contentOffset())
        if blockRect.bottom() >= mouseEvent.y():  # clicked not lower, then end of text
            self.blockClicked.emit(block)
