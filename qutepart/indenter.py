"""Module indentation for block
"""

def getIndenter(languageName, indentText):
    if languageName == 'Python':
        return IndenterPython(indentText)
    else:
        return IndenterNormal(indentText)


class IndenterNormal:
    """Class automatically computes indentation for lines
    This is basic indenter, which knows nothing about programming languages
    """
    def __init__(self, indentText):
        self._indentText = indentText
    
    @staticmethod
    def _prevNonEmptyLineText(block):
        """Return text previous block, which is non empty (contains something, except spaces)
        Return '', if not found
        """
        prevBlock = block.previous()
        
        while prevBlock.isValid() and not prevBlock.text().strip():  # try to find non-empty block
            prevBlock = prevBlock.previous()
        
        return prevBlock.text()

    @staticmethod
    def _lineIndent(text):
        return text[:len(text) - len(text.lstrip())]
    
    def _prevBlockIndent(self, block):
        prevLineText = self._prevNonEmptyLineText(block)
        
        if not prevLineText:
            return ''
        
        return self._lineIndent(prevLineText)

    def computeIndent(self, block):
        """Compute indent for block
        """
        return self._prevBlockIndent(block)
    

class IndenterPython(IndenterNormal):
    """Indenter for Python language.
    """
    def computeIndent(self, block):
        prevLineText = self._prevNonEmptyLineText(block)
        
        if not prevLineText:
            return ''
        
        prevIndent = self._lineIndent(prevLineText)
        prevLineStripped = prevLineText.strip()
        lastCharacter = prevLineText[-1]
        
        """ TODO can detect, what is a code
        if not document.isCode(end of line) and not prevLineText.endswith('"') and not prevLineText.endswith("'"):
            return self._lineIndent(prevLineText)
        """
        # for:
        if lastCharacter == ':':
            return prevIndent + self._indentText
        
        """ Generally, when a brace is on its own at the end of a regular line
        (i.e a data structure is being started), indent is wanted.
        For example:
        dictionary = {
            'foo': 'bar',
        }
        """
        if lastCharacter == '{' or lastCharacter == '[':
            return prevIndent + self._indentText

        # finally, a raise, pass, and continue should unindent
        if prevLineStripped in ('continue', 'pass', 'raise', 'return') or \
           prevLineStripped.startswith('raise ') or \
           prevLineStripped.startswith('return '):
            if prevIndent.endswith(self._indentText):
                return prevIndent[:-len(self._indentText)]
            else:  # oops, strange indentation, just return previous indent
                return prevIndent

        return prevIndent
