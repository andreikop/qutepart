from qutepart.indenter.base import IndenterBase

import re

# Indent after lines that match this regexp
rxIndent = re.compile('^\s*(def|if|unless|for|while|until|class|module|else|elsif|case|when|begin|rescue|ensure|catch)\b')

# Unindent lines that match this regexp
rxUnindent = re.compile('^\s*((end|when|else|elsif|rescue|ensure)\b|[\]\}])(.*)$')


class Statement:
    def __init__(self, startBlock, endBlock):
        self.startBlock = startBlock
        self.endBlock = endBlock
    
    # Convert to string for debugging
    def toString(self):
        return "{ %d, %d}" % (self.startBlock.blockNumber(), self.endBlock.blockNumber())
    
    def offsetToCursor(self, offset):
        # Return an object having 'line' and 'column' set to the given offset in a statement
        # TODO Provide helper function for this when API is converted to using cursors:
        block = self.startBlock
        while block != self.endBlock and \
              len(block.text()) < offset:
            offset -= len(block.text()) + 1
            block = block.next()
        
        return block, offset
  
    def isCode(self, offset):
        # Return document.isCode at the given offset in a statement
        block, column = self.offsetToCursor(offset)
        return document.isCode(block, column)
  
    def isComment(self, offset):
        # Return document.isComment at the given offset in a statement
        block, column = self.offsetToCursor(offset)
        return document.isComment(block, column)
  
    def indent(self):
        # Return the indent at the beginning of the statement
        return IndenterRuby._blockIndent(self.startBlock)
  
    def content(self):
        # Return the content of the statement from the document
        cnt = ""
        block = self.startBlock
        while block.blockNumber() <= self.endBlock.blockNumber():
            text = block.text()
            if text.endswith('\\'):
                cnt += text[:-1]
                cnt += ' '
            else:
                cnt += text
        return cnt


class IndenterRuby(IndenterBase):
    """Indenter for Ruby
    """
    TRIGGER_CHARACTERS = "cdefhilnrsuw}]"
    
    @staticmethod
    def _isCommentBlock(block):
        # FIXME use parser markup
        return block.text.startswith('#')
    
    @staticmethod
    def _isComment(block, column):
        # FIXME use parser markup
        textBefore = block.text()[:column + 1]
        return '#' in textBefore
    
    def _prevNonCommentBlock(block):
        """Return the closest non-empty line, ignoring comments
        (result <= line). Return -1 if the document
        """
        block = self._prevNonEmptyBlock(block)
        while block.isValid() and self._isCommentBlock(block):
            block = self._prevNonEmptyBlock(block)
    
    def _isBlockContinuing(block):
        return block.text().endswith('\\')
    
    def _isLastCodeColumn(block, column):
        """Return true if the given column is at least equal to the column that
        contains the last non-whitespace character at the given line, or if
        the rest of the line is a comment.
        """
        return column >= self._lastColumn(block) or \
               self._isComment(block, self._nextNonSpaceColumn(block, column + 1))
      
    def testAtEnd(stmt, rx):
        """Look for a pattern at the end of the statement.
        
        Returns true if the pattern is found, in a position
        that is not inside a string or a comment, and the position +
        the length of the matching part is either the end of the
        statement, or a comment.
        
        The regexp must be global, and the search is continued until
        a match is found, or the end of the string is reached.
        """
        for match in rx.findIter(stmt.content()):
            if stmt.isCode(match.start()):
                if match.end() == len(stmt.content()):
                    return True
                if stmt.isComment(match.end()):
                    return True
        else:
            return False

    def lastAnchor(block, column):
        """Find the last open bracket before the current line.
        Return (block, column, char) or (None, None, None)
        containing the type of bracket.
        """
        currentPos = -1
        currentBlock = None
        currentColumn = None
        currentChar = None
        for char in '({[':
            try:
                foundBlock, foundColumn = self.findBracketBackward(block, column, char)
            except ValueError:
                continue
            else:
                pos = foundBlock.position() + foundColumn
                if pos > currentPos:
                    currentBlock = foundBlock
                    currentColumn = foundColumn
                    currentChar = char
                    currentPos = pos
        
        return currentBlock, currentColumn, currentChar
    
    def isStmtContinuing(self, block):
        #Is there an open parenthesis?
        
        block, column, char = self.lastAnchor(block.next(), 0)
        if block is not None:
            return True
    
        stmt = Statement(block, block)
        rx = re.compile('((\+|\-|\*|\/|\=|&&|\|\||\band\b|\bor\b|,)\s*)')
    
        return self.testAtEnd(stmt, rx)
    
    def findStmtStart(self, block):
        """Return the first line that is not preceded by a "continuing" line.
        Return currBlock if currBlock <= 0
        """
        prevBlock = self._prevNonCommentBlock(block)
        while prevBlock.isValid() and \
              (((prevBlock == block.previous()) and self._isBlockContinuing(prevBlock)) or \
               self.isStmtContinuing(prevBlock)):
            block = prevBlock
            prevBlock = self._prevNonCommentBlock()
        
        return block

    def _isValidTrigger(self, block, ch):
        """check if the trigger characters are in the right context,
        otherwise running the indenter might be annoying to the user
        """
        if ch == "" or ch == "\n":
            return True # Explicit align or new line
    
        match = rxUnindent.match(block.text())
        if match and match.group(3) == "":
            return True
        else:
            return False    
      
    def findPrevStmt(self, block):
        """Returns a tuple that contains the first and last line of the
        previous statement before line.
        """
        stmtEnd = self._prevNonCommentBlock(line)
        stmtStart = self.findStmtStart(stmtEnd)
    
        return Statement(stmtStart, stmtEnd)
    
    def isBlockStart(self, stmt):
        cnt = stmt.content()
        len = cnt.length
    
        if rxIndent.test(cnt):
            return True
    
        rx = re.compile('((\bdo\b|\{)(\s*\|.*\|)?\s*)')
    
        return self.testAtEnd(stmt, rx)
    
    def isBlockEnd(self, stmt):
        cnt = stmt.content()
    
        return rxUnindent.test(cnt)
    
    def findBlockStart(self, line):
        nested = 0
        stmt = Statement(line, line)
        while True:
            if stmt.start < 0:
                return stmt
            stmt = self.findPrevStmt(stmt.start - 1)
            if isBlockEnd(stmt):
                nested += 1
          
            if self.isBlockStart(stmt):
                if nested == 0:
                    return stmt
                else:
                    nested -= 1    
    
    def computeIndent(self, block, ch):
        """indent gets three arguments: line, indentWidth in spaces,
        typed character indent
        """
        if not self._isValidTrigger(line, ch):
            return None
      
        prevStmt = findPrevStmt(block)
        if prevStmt.end < 0:
            return None  # Can't indent the first line
      
        prev = document.prevNonEmptyLine(line)
      
        """ FIXME
        # HACK Detect here documents
        if (document.isAttributeName(prev, document.lineLength(prev)-1, "Ruby:Here Document")) {
          return -1; // HERE-DOCUMENT
        }
        # HACK Detect embedded comments
        if (document.isAttributeName(prev, document.lineLength(prev)-1, "Ruby:Blockcomment")) {
          return -1
        }
        """
      
        prevStmtCnt = prevStmt.content()
        prevStmtInd = prevStmt.indent()
      
        # Are we inside a parameter list, array or hash?
        anch = self.lastAnchor(block, 0)
        if (anch.line >= 0):
            shouldIndent = (anch.line == prevStmt.end) or \
                           self.testAtEnd(prevStmt, re.compile(',\s*'))
            if (not self._isLastCodeColumn(anch.line, anch.column)) or \
                self.lastAnchor(anch.line, anch.column).line >= 0:
                # TODO This is alignment, should force using spaces instead of tabs:
                if shouldIndent:
                    anch.column += 1
                    nextCol = self._nextNonSpaceColumn(anch.line, anch.column)
                    if nextCol > 0 and \
                       (not self._isComment(anch.line, nextCol)):
                        anch.column = nextCol
  
                # Keep indent of previous statement, while aligning to the anchor column
                if len(prevStmtInd) > anch.column:
                    return prevStmtInd
                else:
                    return self._makeIndentFromWidth(anch.column)
            else:
                indent = self._blockIndent(anch.line)
                if shouldIndent:
                    indent = self._increaseIndent(indent)
                return indent
      
        # Handle indenting of multiline statements.
        if (prevStmt.end == line - 1 and _isBlockContinuing(prevStmt.end)) or \
           isStmtContinuing(prevStmt.end):
            if prevStmt.start == prevStmt.end:
                if ch == '' and \
                   len(self._blockIndent(block)) > len(self._blockIndent(prevStmt.end)):
                    return None  # Don't force a specific indent level when aligning manually
                return self._increaseIndent(self._increaseIndent(prevStmtInd))
            else:
                return self._blockIndent(prevStmt.end)
      
        if rxUnindent.match(block.text()):
            startStmt = self.findBlockStart(block)
            if startStmt.start >= 0:
                return startStmt.indent()
            else:
                return None
      
        if self.isBlockStart(prevStmt):
            return self._increaseIndent(prevStmtInd)
        elif re.search('[\[\{]\s*$', prevStmtCnt) is not None:
            return self._increaseIndent(prevStmtInd)
      
        # Keep current
        return prevStmtInd
  
