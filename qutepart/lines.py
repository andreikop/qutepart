"""Lines class.
list-like object for access text document lines
"""

from PyQt4.QtGui import QTextCursor


def _iterateBlocksFrom(block):
    """FIXME remove
    """
    while block.isValid():
        yield block
        block = block.next()


class Lines:
    """list-like object for access text document lines
    """
    def __init__(self, document):
        self._doc = document
    
    def _toList(self):
        """Convert to Python list
        """
        return [block.text() \
                    for block in _iterateBlocksFrom(self._doc.firstBlock())]
    
    def __str__(self):
        """Serialize
        """
        return str(self._toList())
    
    def __len__(self):
        """Get lines count
        """
        return self._doc.blockCount()
    
    def _checkAndConvertIndex(self, index):
        """Check integer index, convert from less than zero notation
        """
        if index < 0:
            index = len(self) + index
        if index < 0 or index >= self._doc.blockCount():
            raise IndexError('Invalid block index', index)
        return index
    
    def __getitem__(self, index):
        """Get item by index
        """
        def _getTextByIndex(blockIndex):
            return self._doc.findBlockByNumber(blockIndex).text()

        if isinstance(index, int):
            index = self._checkAndConvertIndex(index)
            return _getTextByIndex(index)
        elif isinstance(index, slice):
            start, stop, step = index.indices(self._doc.blockCount())
            return [_getTextByIndex(blockIndex) \
                        for blockIndex in range(start, stop, step)]

    def __setitem__(self, index, value):
        """Set item by index
        FIXME one undo action
        """
        def _setBlockText(blockIndex, text):
            cursor = QTextCursor(self._doc.findBlockByNumber(blockIndex))
            cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            cursor.insertText(text)

        if isinstance(index, int):
            index = self._checkAndConvertIndex(index)
            _setBlockText(index, value)
        elif isinstance(index, slice):
            """List of indexes is reversed for make sure 
            not processed indexes are not shifted during document modification
            """
            start, stop, step = index.indices(self._doc.blockCount())
            if step > 0:
                start, stop, step = stop, start, step * -1

            blockIndexes = list(range(start, stop, step))
            
            if len(blockIndexes) != len(value):
                raise ValueError('Attempt to replace %d lines with %d lines' % (len(blockIndexes), len(value)))
            
            for blockIndex, text in zip(blockIndexes, value[::-1]):
                _setBlockText(blockIndex, text)

    def __delitem__(self, index):
        """Delete item by index
        FIXME one undo action
        """
        def _removeBlock(blockIndex):
            block = self._doc.findBlockByNumber(blockIndex)
            if block.next().isValid():  # not the last
                cursor = QTextCursor(block)
                cursor.movePosition(QTextCursor.NextBlock, QTextCursor.KeepAnchor)
            elif block.previous().isValid():  # the last, not the first
                cursor = QTextCursor(block.previous())
                cursor.movePosition(QTextCursor.EndOfBlock)
                cursor.movePosition(QTextCursor.NextBlock, QTextCursor.KeepAnchor)
                cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            else:  # only one block
                cursor = QTextCursor(block)
                cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()

        if isinstance(index, int):
            index = self._checkAndConvertIndex(index)
            _removeBlock(index)
        elif isinstance(index, slice):
            """List of indexes is reversed for make sure 
            not processed indexes are not shifted during document modification
            """
            start, stop, step = index.indices(self._doc.blockCount())
            if step > 0:
                start, stop, step = stop, start, step * -1

            for blockIndex in range(start, stop, step):
                _removeBlock(blockIndex)

    class _Iterator:
        """Blocks iterator. Returns text
        """
        def __init__(self, block):
            self._block = block
        
        def __iter__(self):
            return self
        
        def next(self):
            if self._block.isValid():
                self._block, result = self._block.next(), self._block.text()
                return result
            else:
                raise StopIteration()

    def __iter__(self):
        """Return iterator object
        """
        return self._Iterator(self._doc.firstBlock())

    def append(self, text):
        """Append line to the end
        """
        cursor = QTextCursor(self._doc)
        cursor.movePosition(QTextCursor.End)
        cursor.insertBlock()
        cursor.insertText(text)

    def insert(self, index, text):
        """Insert line to the document
        FIXME one modification
        """
        if index < 0 or index > self._doc.blockCount():
            raise IndexError('Invalid block index', index)
        
        if index != self._doc.blockCount():
            cursor = QTextCursor(self._doc.findBlockByNumber(index))
            cursor.insertText(text)
            cursor.insertBlock()
        else:  # append to the end
            self.append(text)
