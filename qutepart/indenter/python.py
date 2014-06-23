from qutepart.indenter.base import IndentAlgBase


class IndentAlgPython(IndentAlgBase):
    """Indenter for Python language.
    """
    def computeSmartIndent(self, block, char):
        prevIndent = self._prevNonEmptyBlockIndent(block)

        prevNonEmptyBlock = self._prevNonEmptyBlock(block)
        prevLineStripped = prevNonEmptyBlock.text().strip()  # empty text from invalid block is ok

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
        if prevLineStripped.endswith('{') or \
           prevLineStripped.endswith('['):
            return self._increaseIndent(prevIndent)

        """Check hanging indentation
        call_func(x,
                  y,
                  z
        """
        try:
            foundBlock, foundColumn = self.findAnyBracketBackward(prevNonEmptyBlock,
                                                                  prevNonEmptyBlock.length())
        except ValueError:
            pass
        else:
            return self._makeIndentFromWidth(foundColumn + 1)

        """Unindent if hanging indentation finished
        """
        if prevLineStripped and \
           prevLineStripped[-1] in ')]}':
            try:
                foundBlock, foundColumn = self.findBracketBackward(prevNonEmptyBlock,
                                                                   len(prevNonEmptyBlock.text().rstrip()) - 1,
                                                                   prevLineStripped[-1])
            except ValueError:
                pass
            else:
                return self._blockIndent(foundBlock)

        # finally, a raise, pass, and continue should unindent
        if prevLineStripped in ('continue', 'break', 'pass', 'raise', 'return') or \
           prevLineStripped.startswith('raise ') or \
           prevLineStripped.startswith('return '):
            return self._decreaseIndent(prevIndent)

        return prevIndent
