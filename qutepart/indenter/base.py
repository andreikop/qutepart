class IndenterNone:
    """No any indentation
    """
    def __init__(self, indentTextGetter):
        self._indentText = indentTextGetter
    
    def computeIndent(self, block):
        return ''


class IndenterBase(IndenterNone):
    """Base class for indenters
    """
    TRIGGER_CHARACTERS = ""  # indenter is called, when user types Enter of one of trigger chars
    def __init__(self, qpart):
        self._qpart = qpart
    
    def indentBlock(block):
        """Indent the block
        """
        self._setBlockIndent(block, self.computeIndent(block, ''))
    
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

    def _makeIndentFromWidth(self, width):
        """Make indent text with specified with.
        Contains width count of spaces, or tabs and spaces
        """
        if self._qpart.indentUseTabs:
            tabCount, spaceCount = divmod(width, self._qpart.indentWidth)
            return ('\t' * tabCount) + (' ' * spaceCount)
        else:
            return ' ' * width
    
    @staticmethod
    def _setBlockIndent(block, indent):
        """Set blocks indent. Modify text in qpart
        """
        currentIndent = self._blockIndent(block)
        self._qpart.replaceText((block.blockNumber(), 0), len(currentIndent), indent)
    
    @staticmethod
    def _lastNonSpaceChar(block):
        textStripped = block.text().rstrip()
        if textStripped:
            return textStripped[-1]
        else:
            return ''
    
    @staticmethod
    def _firstNonSpaceChar(block):
        textStripped = block.text().lstrip()
        if textStripped:
            return textStripped[0]
        else:
            return ''
    
    @staticmethod
    def _firstNonSpaceColumn(text):
        return len(text) - len(text.lstrip())

    @staticmethod
    def _lastNonSpaceColumn(text):
        return len(text.rstrip())

    @classmethod
    def _lineIndent(cls, text):
        return text[:cls._firstNonSpaceColumn(text)]
    
    @classmethod
    def _blockIndent(cls, block):
        if block.isValid():
            return cls._lineIndent(block.text())
        else:
            return ''
    
    @classmethod
    def _prevBlockIndent(cls, block):
        prevBlock = block.previous()
        
        if not block.isValid():
            return ''

        return cls._lineIndent(prevBlock.text())
    
    @staticmethod
    def _prevNonEmptyBlock(block):
        block = block.previous()
        while block.isValid() and \
              len(block.text().strip()) == 0:
            block = block.previous()
        
        return block


class IndenterNormal(IndenterBase):
    """Class automatically computes indentation for lines
    This is basic indenter, which knows nothing about programming languages
    """
    def computeIndent(self, block):
        """Compute indent for the block
        """
        return self._blockIndent(self._prevNonEmptyBlock(block))
