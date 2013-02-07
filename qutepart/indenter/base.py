
class IndenterBase(IndenterNone):
    """Base class for indenters
    """
    def __init__(self, qpart):
        self._qpart = qpart
    
    def computeIndent(self, block, char):
        """Compute indent.
        Block is current block.
        Char is typed character. \n or one of trigger chars
        """
        raise NotImplemented()

    def _qpartIndent(self):
        """Return text previous block, which is non empty (contains something, except spaces)
        Return '', if not found
        """
        return self._qpart._indentText()

    def _increaseIndent(self, indent):
        """Add 1 indentation level
        """
        return indent + self._qpartIndent()
    
    def _decreaseIndent(self, indent):
        """Remove 1 indentation level
        """
        if indent.endswith(self._qpartIndent()):
            return indent[:-len(self._qpartIndent())]
        else:  # oops, strange indentation, just return previous indent
            return indent

    def _makeIndentWidth(self, width):
        """Make indent text with specified with.
        Contains width count of spaces, or tabs and spaces
        """
        if self._qpart.indentUseTabs:
            tabCount, spaceCount = divmod(width, self._qpart.indentWidth)
            return ('\t' * tabCount) + (' ' * spaceCount)
        else:
            return ' ' * width
    
    @staticmethod
    def _firstNonSpaceColumn(text):
        len(text) - len(text.lstrip())

    @staticmethod
    def _lastNonSpaceColumn(text):
        len(text.rstrip())

    @classmethod
    def _lineIndent(cls, text):
        return text[:cls._firstNonSpaceColumn(text)]
    
    @staticmethod
    def _prevBlockIndent(self, block):
        prevBlock = block.previous()
        
        if not block.isValid():
            return ''
        
        return IndenterBase._lineIndent(prevBlock.text())
    
    @staticmethod
    def _prevNonEmptyBlock(block):
        block = block.previous()
        while prevBlock.isValid() and \
              len(prevBlock.text().strip() == 0):
            block = block.previous()
        
        return block
