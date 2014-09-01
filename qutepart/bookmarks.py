"""Bookmarks functionality implementation"""

from qutepart.qt import Qt
from qutepart.qt import QAction, QIcon, QKeySequence, QTextCursor

import qutepart


class Bookmarks:
    """Bookmarks functionality implementation, grouped in one class
    """
    def __init__(self, qpart, markArea):
        self._qpart = qpart
        self._markArea = markArea
        qpart.toggleBookmarkAction = self._createAction(qpart, "bookmark.png", "Toogle bookmark", 'Ctrl+B',
                                                        self._onToggleBookmark)
        qpart.prevBookmarkAction = self._createAction(qpart, "up.png", "Previous bookmark", 'Alt+PgUp',
                                                      self._onPrevBookmark)
        qpart.nextBookmarkAction = self._createAction(qpart, "down.png", "Next bookmark", 'Alt+PgDown',
                                                      self._onNextBookmark)

        markArea.blockClicked.connect(self._toggleBookmark)

    def _createAction(self, widget, iconFileName, text, shortcut, slot):
        """Create QAction with given parameters and add to the widget
        """
        icon = QIcon(qutepart.getIconPath(iconFileName))
        action = QAction(icon, text, widget)
        action.setShortcut(QKeySequence(shortcut))
        action.setShortcutContext(Qt.WidgetShortcut)
        action.triggered.connect(slot)

        widget.addAction(action)

        return action

    def clear(self, startBlock, endBlock):
        """Clear bookmarks on block range including start and end
        """
        for block in qutepart.iterateBlocksFrom(startBlock):
            self._setBlockMarked(block, False)
            if block == endBlock:
                break

    @staticmethod
    def isBlockMarked(block):
        """Check if block is bookmarked
        """
        return block.userState() == 1

    def _setBlockMarked(self, block, marked):
        """Set block bookmarked
        """
        block.setUserState(1 if marked else -1)

    def _toggleBookmark(self, block):
        self._setBlockMarked(block, not self.isBlockMarked(block))
        self._markArea.update()

    def _onToggleBookmark(self):
        """Toogle Bookmark action triggered
        """
        self._toggleBookmark(self._qpart.textCursor().block())

    def _onPrevBookmark(self):
        """Previous Bookmark action triggered. Move cursor
        """
        for block in qutepart.iterateBlocksBackFrom(self._qpart.textCursor().block().previous()):
            if self.isBlockMarked(block) or \
               block.blockNumber() in self._qpart.lintMarks:
                self._qpart.setTextCursor(QTextCursor(block))
                return

    def _onNextBookmark(self):
        """Previous Bookmark action triggered. Move cursor
        """
        for block in qutepart.iterateBlocksFrom(self._qpart.textCursor().block().next()):
            if self.isBlockMarked(block) or \
               block.blockNumber() in self._qpart.lintMarks:
                self._qpart.setTextCursor(QTextCursor(block))
                return
