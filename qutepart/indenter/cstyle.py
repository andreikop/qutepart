from qutepart.indenter.base import IndenterBase

# User configuration
CFG_INDENT_CASE = True
CFG_INDENT_NAMESPACE = True
CFG_AUTO_INSERT_STAR = True
CFG_SNAP_SLASH = True
CFG_AUTO_INSERT_SLACHES = False
CFG_ACCESS_MODIFIERS = 0

# indent gets three arguments: line, indentwidth in spaces, typed character
# indent

# specifies the characters which should trigger indent, beside the default '\n'
triggerCharacters = "{})/:;#"

DEBUG_MODE = False

def dbg(*args) {
    if (DEBUG_MODE):
        print *args

#global variables and functions

# maximum number of lines we look backwards/forward to find out the indentation
# level (the bigger the number, the longer might be the delay)
MAX_SEARCH_OFFSET_LINES = 128

INDENT_WIDTH = 4
MODE = "C"


def iterateBlocksFrom(block):
    """Generator, which iterates QTextBlocks from block until the End of a document
    But, yields not more than MAX_SEARCH_OFFSET_LINES
    """
    count = 0
    while block.isValid() and count < MAX_SEARCH_OFFSET_LINES:
        yield block
        block = block.next()
        count += 1

def iterateBlocksBackFrom(block):
    """Generator, which iterates QTextBlocks from block until the Start of a document
    But, yields not more than MAX_SEARCH_OFFSET_LINES
    """
    count = 0
    while block.isValid() and count < MAX_SEARCH_OFFSET_LINES:
        yield block
        block = block.previous()
        count += 1


class CStyleIndenter:
    
    def _findTextBackward(self, block, column, needle):
        """Search for a needle and return (block, column)
        Raise ValueError, if not found
        """
        if column is not None:
            index = block.text()[:column].rfind(needle)
        else
            index = block.text().rfind(needle)
        
        if index != -1:
            return block, index
        
        for block in iterateBlocksBackFrom(block.previous()):
            column = block.text().rfind(needle)
            if column != -1:
                return block, column
    
        raise ValueError('Not found')
    
    def _findLeftBrace(self, block, column)
        """Search for a corresponding '{' and return its indentation
        If not found return None
        """
        try:
            block, column = self._findTextBackward(block, column, '{')
        except ValueError:
            return None
        
        try:
            block, column = _tryParenthesisBeforeBrace(block, column)
        except:
            pass # leave previous values
        
        return self._lineIndent(block.text())
    
    def _tryParenthesisBeforeBrace(block, column):
        """ Character at (line, column) has to be a '{'.
        Now try to find the right line for indentation for constructs like:
          if (a == b
              && c == d) { <- check for ')', and find '(', then return its indentation
        Returns input params, if no success, otherwise block and column of '('
        """
        text = block.text().rstrip()
        
        if not text.endswith(')'):
            raise ValueError()
        
        return self._findTextBackward(block, column, '(')
    
    def _trySwitchStatement(self, block)
        """Check for default and case keywords and assume we are in a switch statement.
        Try to find a previous default, case or switch and return its indentation or
        None if not found.
        """
        if not re.match('^\s*(default\s*|case\b.*):', block.text()):
            return None
    
        for block in iterateBlocksBackFrom(block.previous()):
            text = block.text()
            if re.match("^\s*(default\s*|case\b.*):", text) or \
               re.match("^\s*switch\b", text):
                indentation = self._lineIndent(text)
                if (CFG_INDENT_CASE)
                    indentation = self._increaseIndent(indentation)
                dbg("_trySwitchStatement: success in line %d" + block.blockNumber())
                return indentation
        
        return None
    
    def _tryAccessModifiers(self, block):
        """Check for private, protected, public, signals etc... and assume we are in a
        class definition. Try to find a previous private/protected/private... or
        class and return its indentation or null if not found.
        """
        
        if CFG_ACCESS_MODIFIERS < 0:
            return None
    
        if not re.match('^\s*((public|protected|private)\s*(slots|Q_SLOTS)?|(signals|Q_SIGNALS)\s*):\s*$', block.text()):
            return None
    
        try:
            block, column = self._findTextBackward(block, 0, '{')
        except ValueError:
            return None
    
        indentation = self._lineIndent(block.text())
        for i in range(CFG_ACCESS_MODIFIERS):
            indentation = self._increaseIndent(indentation)
    
        dbg("_tryAccessModifiers: success in line %d" % block.blockNumber())
        return indentation
    
    def _tryCComment(self, block)
        """C comment checking. If the previous line begins with a "/*" or a "* ", then
        return its leading white spaces + ' *' + the white spaces after the *
        return: filler string or null, if not in a C comment
        """
        indentation = None
        
        prevNonEmptyBlock = self._prevNonEmptyBlock(block)
        if not prevNonEmptyBlock.isValid():
            return None
        
        prevNonEmptyBlockText = prevNonEmptyBlock.text()
        
        if prevNonEmptyBlockText.endswith('*/'):
            try:
                foundBlock, notUsedColumn = self._findTextBackward(prevNonEmptyBlock, prevNonEmptyBlock.length(), '/*')
            except ValueError:
                foundBlock = None
            
            if foundBlock is not None:
                dbg("_tryCComment: success (1) in line %d" + foundBlock.blockNumber())
                return self._lineIndent(foundBlock.text())
    
        if prevNonEmptyBlock != block.previous():
            # inbetween was an empty line, so do not copy the "*" character
            return None
    
        blockTextStripped = block.text().strip()
        prevBlockTextStripped = prevNonEmptyBlockText.strip()
        
        if prevBlockTextStripped.startswith('/*'):
            indentation = self._blockIndent(prevNonEmptyBlock)
            if CFG_AUTO_INSERT_STAR:
                # only add '*', if there is none yet.
                indentation += self._indentText()
                if not blockTextStripped.endswith('*'):
                    indentation += '*'
                secondCharIsSpace = len(blockTextStripped) > 1 and blockTextStripped[1].isspace()
                if not secondCharIsSpace and \
                   not blockTextStripped.endswith("*/")
                    indentation += ' '
            dbg("_tryCComment: success (2) in line %d" + block.blockNumber())
            return indentation
            
        elif prevBlockTextStripped.startswith('*') and \
             (len(prevBlockTextStripped) == 1 or prevBlockTextStripped[1].isspace()):
            
            # in theory, we could search for opening /*, and use its indentation
            # and then one alignment character. Let's not do this for now, though.
            indentation = self._lineIndent(block.text())
            # only add '*', if there is none yet.
            if CFG_AUTO_INSERT_STAR and not blockTextStripped.startswith('*'):
                indentation += '*'
                if len(blockTextStripped) < 2 or not blockTextStripped[1].isspace():
                    indentation += ' '
            
            dbg("_tryCComment: success (2) in line %d" + block.blockNumber())
            return indentation
    
        return None
    
    def _tryCppComment(self, block):
        """C++ comment checking. when we want to insert slashes:
        #, #/, #! #/<, #!< and ##...
        return: filler string or null, if not in a star comment
        NOTE: otherwise comments get skipped generally and we use the last code-line
        """
        if not block.previous().isValid() or \
           not CFG_AUTO_INSERT_SLACHES:
            return None
        
        prevLineText = block.previous().text()
        
        indentation = None
        comment = prevLineText.lstrip().startswith('#')
    
        # allowed are: #, #/, #! #/<, #!< and ##...
        if comment:
            var firstPos = document.firstColumn(currentLine)
            var prevLineText = document.line(currentLine)
    
            var char3 = prevLineText.charAt(firstPos + 2)
            var char4 = prevLineText.charAt(firstPos + 3)
            
            indentation = self._lineIndent(prevLineText)
    
            if CFG_AUTO_INSERT_SLACHES:
                if prevLineText[2:4] == '//':
                    # match ##... and replace by only two: #
                    match = re.match('^\s*(\/\/)', prevLineText)
                else if (char3 == '/' or char3 == '!'):
                    # match #/, #!, #/< and #!
                    match = re.match('^\s*(\/\/[\/!][<]?\s*)', prevLineText)
                else:
                    # only #, nothing else
                    match = re.match('^\s*(\/\/\s*)', prevLineText)
                
                if match is not None:
                    self._insertText(block.blockNumber(), 0, match.group(1))
    
        if indentation is not None:
            dbg("tryCppComment: success in line %d" % block.previous().blockNumber())
        
        return indentation
    
    def _tryBrace(self, block):
        def _isNamespace(block):
            if not block.text().strip():
                block = block.previous()

            return re.match('^\s*namespace\b', block.text()) is not None
    
        currentBlock = self._prevNonEmptyBlock(block)
        if not currentBlock.isValid():
            return None
    
        indentation = None
    
        if currentBlock.text().endswith('{'):
            try:
                foundBlock, foundColumn = self._tryParenthesisBeforeBrace(currentBlock, len(currentBlock.text().rstrip()))
            except ValueError:
                foundBlock = None
            
            if foundBlock is not None:
                indentation = self._increaseIndent(self._lineIndent(block.text()))
            else:
                indentation = self._lineIndent(block.text())
                if CFG_INDENT_NAMESPACE or not _isNamespace(block))
                    # take its indentation and add one indentation level
                    indentation = self._increaseIndent(indentation)
    
        if indentation is not None:
            dbg("tryBrace: success in line %d" % block.blockNumber())
        return indentation
    
    def _tryCKeywords(block, isBrace):
        """
        Check for if, else, while, do, switch, private, public, protected, signals,
        default, case etc... keywords, as we want to indent then. If   is
        non-null/True, then indentation is not increased.
        Note: The code is written to be called *after* _tryCComment and tryCppComment!
        """
        currentBlock = self._prevNonEmptyBlock(block)
        if not currentBlock.isValid():
            return None
            
        # if line ends with ')', find the '(' and check this line then.
        var lastPos = document.lastColumn(currentLine)
        var cursor = new Cursor().invalid()
        
        if currentBlock.text().rstrip().endswith(')'):
            try:
                foundBlock, foundColumn = self._findTextBackward(block, currentBlock, len(currentBlock.text()), '(')
            except ValueError:
                pass
            else:
                currentBlock = foundBlock
        
        # found non-empty line
        currentBlockText = currentBlock.text()
        if re.search('^\s*(if\b|for|do\b|while|switch|[}]?\s*else|((private|public|protected|case|default|signals|Q_SIGNALS).*:))', currentBlockText) is None:
            return None
        
        indentation = None
    
        # ignore trailing comments see: https:#bugs.kde.org/show_bug.cgi?id=189339
        try:
            index = currentBlockText.index('#')
        except ValueError:
            pass
        else:
            currentBlockText = currentBlockText[:index]
    
        # try to ignore lines like: if (a) b; or if (a) { b; }
        if not currentBlockText.endswith(';') and \
           not currentBlockText.endswith('}'):
            indentation = self._blockIndent(currentBlock)
            if not isBrace:
                indentation = self._increaseIndent(indentation)
        elif currentBlockText.endswith(';'):
            # stuff like:
            # for(int b
            #     b < 10
            #     --b)
            try:
                foundBlock, foundColumn = self._findTextBackward(currentBlock, None, '(')
            except ValueError:
                pass
            else:
                return _makeIndentWidth(foundColumn + 1)

    def _tryCondition(self, block)
        """ Search for if, do, while, for, ... as we want to indent then.
        Return null, if nothing useful found.
        Note: The code is written to be called *after* _tryCComment and tryCppComment!
        """
        currentBlock = self._prevNonEmptyBlock(block)
        if not currentBlock.isValid():
            return None
    
        # found non-empty line
        currentText = block.text()
    
        if currentText.rstrip().endswith(';') and \
           re.match('^\s*(if\b|[}]?\s*else|do\b|while\b|for)', None):
            # idea: we had something like:
            #   if/while/for (expression)
            #       statement();  <-- we catch this trailing ';'
            # Now, look for a line that starts with if/for/while, that has one
            # indent level less.
            currentIndentation = self._lineIndent(currentText)
            if not currentIndentation:
                return None
            
            for block in iterateBlocksBackFrom(currentBlock.previous()):
                if block.strip(): # not empty
                    blockIndent = self._blockIndent(block)
                        
                    if len(blockIndent) < len(currentIndentation)
                        if re.search('^\s*(if\b|[}]?\s*else|do\b|while\b|for)[^{]*$', block.text()) is not None:
                            return blockIndent
        
        return None
    
    /**
     * If the non-empty line ends with ); or ',', then search for '(' and return its
     * indentation; also try to ignore trailing comments.
     */
    def tryStatement(line)
    {
        var currentLine = self._prevNonEmptyBlock(line - 1).text()
        if (currentLine < 0)
            return -1
    
        var indentation = -1
        var currentString = document.line(currentLine)
        if (currentString.endswith('(')) {
            # increase indent level
            indentation = document.firstVirtualColumn(currentLine) + INDENT_WIDTH
            dbg("tryStatement: success in line " + currentLine)
            return indentation
        }
        var alignOnSingleQuote = MODE == "PHP/PHP" or MODE == "JavaScript"
        # align on strings "..."\n => below the opening quote
        # multi-language support: [\.+] for javascript or php
        var result = /^(.*)(,|"|'|\))(;?)\s*[\.+]?\s*(\/\/.*|\/\*.*\*\/\s*)?$/.exec(currentString)
        if (result != null && result.index == 0) {
            var alignOnAnchor = result[3].length == 0 && result[2] != ')'
            # search for opening ", ' or (
            var cursor = new Cursor().invalid()
            if (result[2] == '"' or (alignOnSingleQuote && result[2] == "'")) {
                whileTrue {
                    var i = result[1].length - 1; # start from matched closing ' or "
                    # find string opener
                    for ( ; i >= 0; --i ) {
                        # make sure it's not commented out
                        if (currentString[i] == result[2] && (i == 0 or currentString[i - 1] != '\\')) {
                            # also make sure that this is not a line like '#include "..."' <-- we don't want to indent here
                            if (currentString.match(/^#include/)) {
                                return indentation
                            }
                            cursor = new Cursor(currentLine, i)
                            break
                        }
                    }
                    if (!alignOnAnchor && currentLine) {
                        # when we finished the statement (;) we need to get the first line and use it's indentation
                        # i.e.: $foo = "asdf"; -> align on $
                        --i; # skip " or '
                        # skip whitespaces and stuff like + or . (for PHP, JavaScript, ...)
                        for ( ; i >= 0; --i ) {
                            if (currentString[i] == ' ' or currentString[i] == "\t"
                                or currentString[i] == '.' or currentString[i] == '+')
                            {
                                continue
                            } else {
                                break
                            }
                        }
                        if ( i > 0 ) {
                            # there's something in this line, use it's indentation
                            break
                        } else {
                            # go to previous line
                            --currentLine
                            currentString = document.line(currentLine)
                        }
                    } else {
                        break
                    }
                }
            } else if (result[2] == ',' && !currentString.match(/\(/)) {
                # assume a function call: check for '(' brace
                # - if not found, use previous indentation
                # - if found, compare the indentation depth of current line and open brace line
                #   - if current indentation depth is smaller, use that
                #   - otherwise, use the '(' indentation + following white spaces
                var currentIndentation = document.firstVirtualColumn(currentLine)
                var braceCursor = document.anchor(currentLine, result[1].length, '(')
    
                if (!braceCursor.isValid() or currentIndentation < braceCursor.column)
                    indentation = currentIndentation
                else {
                    indentation = braceCursor.column + 1
                    while (document.isSpace(braceCursor.line, indentation))
                        ++indentation
                }
            } else {
                cursor = document.anchor(currentLine, result[1].length, '(')
            }
            if (cursor.isValid()) {
                if (alignOnAnchor) {
                    currentLine = cursor.line
                    var column = cursor.column
                    if (result[2] != '"' && result[2] != "'") {
                        # place one column after the opening parens
                        column++
                    }
                    var lastColumn = document.lastColumn(currentLine)
                    while (column < lastColumn && document.isSpace(currentLine, column))
                        ++column
                    indentation = document.toVirtualColumn(currentLine, column)
                } else {
                    currentLine = cursor.line
                    indentation = document.firstVirtualColumn(currentLine)
                }
            }
        } else if ( currentString.rtrim().endswith(';') ) {
            indentation = document.firstVirtualColumn(currentLine)
        }
    
        if (indentation != -1) dbg("tryStatement: success in line " + currentLine)
        return indentation
    }
    
    /**
     * find out whether we pressed return in something like {} or () or [] and indent properly:
     * {}
     * becomes:
     * {
     *   |
     * }
     */
    def tryMatchedAnchor(line, alignOnly)
    {
        var char = document.firstChar(line)
        if ( char != '}' && char != ')' && char != ']' ) {
            return -1
        }
        # we pressed enter in e.g. ()
        var closingAnchor = document.anchor(line, 0, document.firstChar(line))
        if (!closingAnchor.isValid()) {
            # nothing found, continue with other cases
            return -1
        }
        if (alignOnly) {
            # when aligning only, don't be too smart and just take the indent level of the open anchor
            return document.firstVirtualColumn(closingAnchor.line)
        }
        var lastChar = document.lastChar(line - 1)
        var charsMatch = ( lastChar == '(' && char == ')' ) or
                         ( lastChar == '{' && char == '}' ) or
                         ( lastChar == '[' && char == ']' )
        var indentLine = -1
        var indentation = -1
        if ( !charsMatch && char != '}' ) {
            # otherwise check whether the last line has the expected
            # indentation, if not use it instead and place the closing
            # anchor on the level of the openeing anchor
            var expectedIndentation = document.firstVirtualColumn(closingAnchor.line) + INDENT_WIDTH
            var actualIndentation = document.firstVirtualColumn(line - 1)
            var indentation = -1
            if ( expectedIndentation <= actualIndentation ) {
                if ( lastChar == ',' ) {
                    # use indentation of last line instead and place closing anchor
                    # in same column of the openeing anchor
                    document.insertText(line, document.firstColumn(line), "\n")
                    view.setCursorPosition(line, actualIndentation)
                    # indent closing anchor
                    document.indent(new Range(line + 1, 0, line + 1, 1), document.toVirtualColumn(closingAnchor) / INDENT_WIDTH)
                    # make sure we add spaces to align perfectly on closing anchor
                    var padding = document.toVirtualColumn(closingAnchor) % INDENT_WIDTH
                    if ( padding > 0 ) {
                        document.insertText(line + 1, document.column - padding, String().fill(' ', padding))
                    }
                    indentation = actualIndentation
                } else if ( expectedIndentation == actualIndentation ) {
                    # otherwise don't add a new line, just use indentation of closing anchor line
                    indentation = document.firstVirtualColumn(closingAnchor.line)
                } else {
                    # otherwise don't add a new line, just align on closing anchor
                    indentation = document.toVirtualColumn(closingAnchor)
                }
                dbg("tryMatchedAnchor: success in line " + closingAnchor.line)
                return indentation
            }
        }
        # otherwise we i.e. pressed enter between (), [] or when we enter before curly brace
        # increase indentation and place closing anchor on the next line
        indentation = document.firstVirtualColumn(closingAnchor.line)
        document.insertText(line, document.firstColumn(line), "\n")
        view.setCursorPosition(line, indentation)
        # indent closing brace
        document.indent(new Range(line + 1, 0, line + 1, 1), indentation / INDENT_WIDTH)
        dbg("tryMatchedAnchor: success in line " + closingAnchor.line)
        return indentation + INDENT_WIDTH
    }
    
    /**
     * Indent line.
     * Return filler or null.
     */
    def indentLine(line, alignOnly)
    {
        var firstChar = document.firstChar(line)
        var lastChar = document.lastChar(line)
    
        var filler = -1
    
        if (filler == -1)
            filler = tryMatchedAnchor(line, alignOnly)
        if (filler == -1)
            filler = _tryCComment(line)
        if (filler == -1 && !alignOnly)
            filler = tryCppComment(line)
        if (filler == -1)
            filler = _trySwitchStatement(line)
        if (filler == -1)
            filler = _tryAccessModifiers(line)
        if (filler == -1)
            filler = tryBrace(line)
        if (filler == -1)
            filler = tryCKeywords(line, firstChar == '{')
        if (filler == -1)
            filler = tryCondition(line)
        if (filler == -1)
            filler = tryStatement(line)
    
        return filler
    }
    
    def processChar(line, c)
    {
        if (c == ';' or !triggerCharacters.contains(c))
            return -2
    
        var cursor = view.cursorPosition()
        if (!cursor)
            return -2
    
        var column = cursor.column
        var firstPos = document.firstColumn(line)
        var lastPos = document.lastColumn(line)
    
         dbg("firstPos: " + firstPos)
         dbg("column..: " + column)
    
        if (firstPos == column - 1 && c == '{') {
            # todo: maybe look for if etc.
            var filler = tryBrace(line)
            if (filler == -1)
                filler = tryCKeywords(line, True)
            if (filler == -1)
                filler = _tryCComment(line); # checks, whether we had a "*/"
            if (filler == -1)
                filler = tryStatement(line)
            if (filler == -1)
                filler = -2
    
            return filler
        } else if (firstPos == column - 1 && c == '}') {
            var indentation = _findLeftBrace(line, firstPos)
            if (indentation == -1)
                indentation = -2
            return indentation
        } else if (CFG_SNAP_SLASH && c == '/' && lastPos == column - 1) {
            # try to snap the string "* /" to "*/"
            var currentString = document.line(line)
            if (currentString.search(/^(\s*)\*\s+\/\s*$/) != -1) {
                currentString = RegExp.$1 + "*/"
                document.editBegin()
                document.removeLine(line)
                document.insertLine(line, currentString)
                view.setCursorPosition(line, currentString.length)
                document.editEnd()
            }
            return -2
        } else if (c == ':') {
            # todo: handle case, default, signals, private, public, protected, Q_SIGNALS
            var filler = _trySwitchStatement(line)
            if (filler == -1)
                filler = _tryAccessModifiers(line)
            if (filler == -1)
                filler = -2
            return filler
        } else if (c == ')' && firstPos == column - 1) {
            # align on start of identifier of function call
            var openParen = document.anchor(line, column - 1, '(')
            if (openParen.isValid()) {
                # get identifier
                var callLine = document.line(openParen.line)
                # strip starting from opening paren
                callLine = callLine.substring(0, openParen.column - 1)
                indentation = callLine.search(/\b(\w+)\s*$/)
                if (indentation != -1) {
                    return document.toVirtualColumn(openParen.line, indentation)
                }
            }
        } else if (firstPos == column - 1 && c == '#' && ( MODE == 'C' or MODE == 'C++' ) ) {
            # always put preprocessor stuff upfront
            return 0
        }
        return -2
    }
    
    /**
     * Process a newline character.
     * This function is called whenever the user hits <return/enter>.
     */
    def indent(line, indentWidth, ch)
    {
        INDENT_WIDTH = indentWidth
        MODE = document.highlightinMODEAt(new Cursor(line, document.lineLength(line)))
        var alignOnly = (ch == "")
    
        if (ch != '\n' && !alignOnly)
            return processChar(line, ch)
    
        return indentLine(line, alignOnly)
    }
    
    # kate: space-indent on; indent-width 4; replace-tabs on
