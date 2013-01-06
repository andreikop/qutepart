"""Bracket highlighter.
Calculates list of QTextEdit.ExtraSelection
"""

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTextCursor, QTextEdit


class BracketHighlighter:
    """Bracket highliter.
    Calculates list of QTextEdit.ExtraSelection
    
    Currently, this class might be just a set of functions.
    Probably, it will contain instance specific selection colors later
    """
    
    _startBrackets  = '({['
    _endBrackets = ')}]'
    _allBrackets = _startBrackets + _endBrackets
    _opositeBracket = dict( (bracket, oposite)
                    for (bracket, oposite) in zip(_startBrackets + _endBrackets, _endBrackets + _startBrackets))
    
    @staticmethod
    def _iterateDocumentCharsForward(block, startColumnIndex):
        """Traverse document forward. Yield (block, columnIndex, char)
        """
        for columnIndex, char in list(enumerate(block.text()))[startColumnIndex:]:
            yield block, columnIndex, char
        block = block.next()
        
        while block.isValid():
            for columnIndex, char in enumerate(block.text()):
                yield block, columnIndex, char
            block = block.next()
    
    @staticmethod
    def _iterateDocumentCharsBackward(block, startColumnIndex):
        """Traverse document forward. Yield (block, columnIndex, char)
        """
        for columnIndex, char in reversed(list(enumerate(block.text()[:startColumnIndex]))):
            yield block, columnIndex, char
        block = block.previous()
        
        while block.isValid():
            for columnIndex, char in reversed(list(enumerate(block.text()))):
                yield block, columnIndex, char
            block = block.previous()
    
    def _findMatchingBracket(self, bracket, block, columnIndex):
        """Find matching bracket for the bracket.
        Return (block, columnIndex) or (None, None)
        TODO improve this method sometimes for skipping strings and comments
        """
        if bracket in self._startBrackets:
            charsGenerator = self._iterateDocumentCharsForward(block, columnIndex + 1)
        else:
            charsGenerator = self._iterateDocumentCharsBackward(block, columnIndex)

        depth = 1
        oposite = self._opositeBracket[bracket]
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
        selection.cursor.setPosition(block.position() + columnIndex)
        selection.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
        
        return selection

    def _highlightBracket(self, bracket, block, columnIndex):
        """Highlight bracket and matching bracket
        Return tuple of QTextEdit.ExtraSelection's
        """
        matchedBlock, matchedColumnIndex = self._findMatchingBracket(bracket, block, columnIndex)
        if matchedBlock is not None:
            return [self._makeMatchSelection(block, columnIndex, True),
                    self._makeMatchSelection(matchedBlock, matchedColumnIndex, True)]
        else:
            return [self._makeMatchSelection(block, columnIndex, False)]
    
    def extraSelections(self, block, columnIndex):
        """List of QTextEdit.ExtraSelection's, which highlighte brackets
        """
        blockText = block.text()
        
        if columnIndex > 0 and blockText[columnIndex - 1] in self._allBrackets:
            return self._highlightBracket(blockText[columnIndex - 1], block, columnIndex - 1)
        elif columnIndex < len(blockText) and blockText[columnIndex] in self._allBrackets:
            return self._highlightBracket(blockText[columnIndex], block, columnIndex)
        else:
            return []