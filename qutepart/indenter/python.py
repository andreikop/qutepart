from qutepart.indenter.base import IndenterBase

class IndenterPython(IndenterBase):
    """Indenter for Python language.
    """
    def computeIndent(self, block, char):
        prevIndent = self._prevBlockIndent(block)
        
        prevLineStripped = block.previous().text().strip()  # empty text from invalid block is ok
        
        """ TODO can detect, what is a code
        if not document.isCode(end of line) and not prevLineText.endswith('"') and not prevLineText.endswith("'"):
            return self._lineIndent(prevLineText)
        """
        # for:
        if prevLineStripped.endswith(':'):
            return self._increaseIndent(prevIndent)
        
        """ Generally, when a brace is on its own at the end of a regular line
        (i.e a data structure is being started), indent is wanted.
        For example:
        dictionary = {
            'foo': 'bar',
        }
        """
        if prevLineStripped.endswith('{') or prevLineStripped.endswith('['):
            return self._increaseIndent(prevIndent)

        # finally, a raise, pass, and continue should unindent
        if prevLineStripped in ('continue', 'pass', 'raise', 'return') or \
           prevLineStripped.startswith('raise ') or \
           prevLineStripped.startswith('return '):
            return self._decreaseIndent(prevIndent)

        return prevIndent
