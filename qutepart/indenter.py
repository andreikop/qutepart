"""Module computes indentation for block
It contains implementation of indenters, which are supported by katepart xml files
"""

import re

def getIndenter(indenterName, indentTextGetter):
    """Get indenter by name.
    Available indenters are none, normal, cstyle, haskell, lilypond, lisp, python, ruby, xml
    Indenter name is not case sensitive
    Raise KeyError if not found
    indentText is indentation, which shall be used. i.e. '\t' for tabs, '    ' for 4 space symbols
    """
    indenters = {
        'none' : IndenterNone,
        'normal' : IndenterNormal,
        'cstyle' : IndenterCStyle,
        'haskell' : IndenterHaskell,
        'lilypond' : IndenterLilypond,
        'lisp' : IndenterLisp,
        'python' : IndenterPython,
        'ruby' : IndenterRuby
    }
    
    indenterClass = indenters[indenterName.lower()]  # KeyError is ok, raise it up
    
    return indenterClass(indentTextGetter)


class IndenterNone:
    """No any indentation
    """
    def __init__(self, indentTextGetter):
        self._indentText = indentTextGetter
    
    def computeIndent(self, block):
        return ''


class IndenterNormal(IndenterNone):
    """Class automatically computes indentation for lines
    This is basic indenter, which knows nothing about programming languages
    """
    @staticmethod
    def _prevLineText(block):
        """Return text previous block, which is non empty (contains something, except spaces)
        Return '', if not found
        """
        prevBlock = block.previous()
        return block.previous().text()

    @staticmethod
    def _prevNonEmptyLineText(block):
        """Return text previous block, which is non empty (contains something, except spaces)
        Return '', if not found
        """
        block = block.previous()
        while prevBlock.isValid() and \
              len(prevBlock.text().strip() == 0):
            block = block.previous()
        
        if block.isValid():
            return block.text()
        else:
            return ''

    @staticmethod
    def _lineIndent(text):
        return text[:len(text) - len(text.lstrip())]
    
    def _removeIndent(self, text):
        """Remove 1 indentation level
        """
        if text.endswith(self._indentText()):
            return text[:-len(self._indentText())]
        else:  # oops, strange indentation, just return previous indent
            return text

    
    def _prevBlockIndent(self, block):
        prevLineText = self._prevLineText(block)
        
        if not prevLineText:
            return ''
        
        return self._lineIndent(prevLineText)

    def computeIndent(self, block):
        """Compute indent for the block
        """
        return self._prevBlockIndent(block)

class IndenterCStyle(IndenterNormal):
    """TODO implement
    """
    pass


class IndenterHaskell(IndenterNormal):
    """TODO implement
    """
    pass


class IndenterLilypond(IndenterNormal):
    """TODO implement
    """
    pass


class IndenterLisp(IndenterNormal):
    """TODO implement
    """
    pass


class IndenterPython(IndenterNormal):
    """Indenter for Python language.
    """
    def computeIndent(self, block):
        prevLineText = self._prevLineText(block)
        
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
            return prevIndent + self._indentText()
        
        """ Generally, when a brace is on its own at the end of a regular line
        (i.e a data structure is being started), indent is wanted.
        For example:
        dictionary = {
            'foo': 'bar',
        }
        """
        if lastCharacter == '{' or lastCharacter == '[':
            return prevIndent + self._indentText()

        # finally, a raise, pass, and continue should unindent
        if prevLineStripped in ('continue', 'pass', 'raise', 'return') or \
           prevLineStripped.startswith('raise ') or \
           prevLineStripped.startswith('return '):
            return self._removeIndent(prevIndent)

        return prevIndent


class IndenterRuby(IndenterNormal):
    """TODO implement
    """
    pass
