# maximum number of lines we look backwards/forward to find out the indentation
# level (the bigger the number, the longer might be the delay)
MAX_SEARCH_OFFSET_LINES = 128


class IndenterNone:
    """No any indentation
    """
    def __init__(self, qpart):
        pass
    
    def computeIndent(self, block, char):
        return ''


class IndenterBase(IndenterNone):
    """Base class for indenters
    """
    TRIGGER_CHARACTERS = ""  # indenter is called, when user types Enter of one of trigger chars
    def __init__(self, qpart):
        self._qpart = qpart
    
    def indentBlock(self, block):
        """Indent the block
        """
        self._setBlockIndent(block, self.computeIndent(block, ''))
    
    def computeIndent(self, block, char):
        """Compute indent.
        Block is current block.
        Char is typed character. \n or one of trigger chars
        Return indentation text, or None, if indentation shall not be modified
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
    
    def _setBlockIndent(self, block, indent):
        """Set blocks indent. Modify text in qpart
        """
        currentIndent = self._blockIndent(block)
        self._qpart.replaceText((block.blockNumber(), 0), len(currentIndent), indent)
    
    @staticmethod
    def iterateBlocksFrom(block):
        """Generator, which iterates QTextBlocks from block until the End of a document
        But, yields not more than MAX_SEARCH_OFFSET_LINES
        """
        count = 0
        while block.isValid() and count < MAX_SEARCH_OFFSET_LINES:
            yield block
            block = block.next()
            count += 1
    
    @staticmethod
    def iterateBlocksBackFrom(block):
        """Generator, which iterates QTextBlocks from block until the Start of a document
        But, yields not more than MAX_SEARCH_OFFSET_LINES
        """
        count = 0
        while block.isValid() and count < MAX_SEARCH_OFFSET_LINES:
            yield block
            block = block.previous()
            count += 1
    
    @classmethod
    def iterateCharsBackwardFrom(cls, block, column):
        if column is not None:
            text = block.text()[:column]
            for index, char in enumerate(reversed(text)):
                yield block, len(text) - index - 1, char
            block = block.previous()
        
        for block in cls.iterateBlocksBackFrom(block):
            for index, char in enumerate(reversed(block.text())):
                yield block, len(block.text()) - index - 1, char
    
    def findBracketBackward(self, block, column, bracket):
        """Search for a needle and return (block, column)
        Raise ValueError, if not found
        """
        if bracket in ('(', ')'):
            opening = '('
            closing = ')'
        elif bracket in ('[', ']'):
            opening = '['
            closing = ']'
        elif bracket in ('{', '}'):
            opening = '{'
            closing = '}'
        else:
            raise AssertionError('Invalid bracket "%s"' % bracket)
        
        depth = 1
        for foundBlock, foundColumn, char in self.iterateCharsBackwardFrom(block, column):
            if not self._qpart.isComment(foundBlock.blockNumber(), foundColumn):
                if char == opening:
                    depth = depth - 1
                elif char == closing:
                    depth = depth + 1
                
                if depth == 0:
                    return foundBlock, foundColumn
        else:
            raise ValueError('Not found')

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
        if not block.isValid():
            return block
        
        block = block.previous()
        while block.isValid() and \
              len(block.text().strip()) == 0:
            block = block.previous()
        return block
    
    @staticmethod
    def _nextNonEmptyBlock(block):
        if not block.isValid():
            return block
        
        block = block.next()
        while block.isValid() and \
              len(block.text().strip()) == 0:
            block = block.next()
        return block
    
    def _lastColumn(self, block):
        """Returns the last non-whitespace column in the given line.
        If there are only whitespaces in the line, the return value is -1.
        """
        text = block.text()
        index = len(block.text()) - 1
        while index >= 0 and \
              (text[index].isspace() or \
               self._qpart.isComment(block.blockNumber(), index)):
            index -= 1
        
        return index
    
    @staticmethod
    def _nextNonSpaceColumn(block, column):
        """Returns the column with a non-whitespace characters 
        starting at the given cursor position and searching forwards.
        """
        textAfter = block.text()[column:]
        if textAfter.strip():
            spaceLen = len(textAfter) - len(textAfter.lstrip())
            return column + spaceLen
        else:
            return -1


class IndenterNormal(IndenterBase):
    """Class automatically computes indentation for lines
    This is basic indenter, which knows nothing about programming languages
    """
    def computeIndent(self, block, char):
        """Compute indent for the block
        """
        return self._blockIndent(self._prevNonEmptyBlock(block))
