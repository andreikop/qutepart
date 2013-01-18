"""Bracket highlighter.
Calculates list of QTextEdit.ExtraSelection
"""

import time

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTextCursor, QTextEdit


class BracketHighlighter:
    """Bracket highliter.
    Calculates list of QTextEdit.ExtraSelection
    
    Currently, this class might be just a set of functions.
    Probably, it will contain instance specific selection colors later
    """
    _MAX_SEARCH_TIME_SEC = 0.02
    
    _START_BRACKETS = '({['
    _END_BRACKETS = ')}]'
    _ALL_BRACKETS = _START_BRACKETS + _END_BRACKETS
    _OPOSITE_BRACKET = dict( (bracket, oposite)
                    for (bracket, oposite) in zip(_START_BRACKETS + _END_BRACKETS, _END_BRACKETS + _START_BRACKETS))
    
    def _iterateDocumentCharsForward(self, block, startColumnIndex):
        """Traverse document forward. Yield (block, columnIndex, char)
        Raise UserWarning if time is over
        """
        # Chars in the start line
        endTime = time.clock() + self._MAX_SEARCH_TIME_SEC
        for columnIndex, char in list(enumerate(block.text()))[startColumnIndex:]:
            yield block, columnIndex, char
        block = block.next()
        
        # Next lines
        while block.isValid():
            for columnIndex, char in enumerate(block.text()):
                yield block, columnIndex, char
            
            if time.clock() > endTime:
                raise UserWarning('Time is over')
            
            block = block.next()
    
    def _iterateDocumentCharsBackward(self, block, startColumnIndex):
        """Traverse document forward. Yield (block, columnIndex, char)
        Raise UserWarning if time is over
        """
        # Chars in the start line
        endTime = time.clock() + self._MAX_SEARCH_TIME_SEC
        for columnIndex, char in reversed(list(enumerate(block.text()[:startColumnIndex]))):
            yield block, columnIndex, char
        block = block.previous()
        
        # Next lines
        while block.isValid():
            for columnIndex, char in reversed(list(enumerate(block.text()))):
                yield block, columnIndex, char
            
            if time.clock() > endTime:
                raise UserWarning('Time is over')
            
            block = block.previous()
    
    def _findMatchingBracket(self, bracket, block, columnIndex):
        """Find matching bracket for the bracket.
        Return (block, columnIndex) or (None, None)
        Raise UserWarning, if time is over
        TODO improve this method sometimes for skipping strings and comments
        """
        if bracket in self._START_BRACKETS:
            charsGenerator = self._iterateDocumentCharsForward(block, columnIndex + 1)
        else:
            charsGenerator = self._iterateDocumentCharsBackward(block, columnIndex)

        depth = 1
        oposite = self._OPOSITE_BRACKET[bracket]
        for block, columnIndex, char in charsGenerator:
            if char == oposite:
                depth -= 1
                if depth == 0:
                    return block, columnIndex
            elif char == bracket:
                depth += 1
        else:
            return None, None
    
    def _makeMatchSelection(self, block, columnIndex, matched):
        """Make matched or unmatched QTextEdit.ExtraSelection
        """
        selection = QTextEdit.ExtraSelection()

        if matched:
            bgColor = Qt.green
        else:
            bgColor = Qt.red
        
        selection.format.setBackground(bgColor)
        selection.cursor = QTextCursor(block)
        selection.cursor.setPositionInBlock(columnIndex)
        selection.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
        
        return selection

    def _highlightBracket(self, bracket, block, columnIndex):
        """Highlight bracket and matching bracket
        Return tuple of QTextEdit.ExtraSelection's
        """
        try:
            matchedBlock, matchedColumnIndex = self._findMatchingBracket(bracket, block, columnIndex)
        except UserWarning:  # not found, time is over
            return[] # highlight nothing
        
        if matchedBlock is not None:
            return [self._makeMatchSelection(block, columnIndex, True),
                    self._makeMatchSelection(matchedBlock, matchedColumnIndex, True)]
        else:
            return [self._makeMatchSelection(block, columnIndex, False)]
    
    def extraSelections(self, block, columnIndex):
        """List of QTextEdit.ExtraSelection's, which highlighte brackets
        """
        blockText = block.text()
        
        if columnIndex > 0 and blockText[columnIndex - 1] in self._ALL_BRACKETS:
            return self._highlightBracket(blockText[columnIndex - 1], block, columnIndex - 1)
        elif columnIndex < len(blockText) and blockText[columnIndex] in self._ALL_BRACKETS:
            return self._highlightBracket(blockText[columnIndex], block, columnIndex)
        else:
            return []
