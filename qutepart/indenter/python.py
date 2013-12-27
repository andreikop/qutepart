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
            print 'case 2'
            return self._increaseIndent(prevIndent)

        # finally, a raise, pass, and continue should unindent
        if prevLineStripped in ('continue', 'break', 'pass', 'raise', 'return') or \
           prevLineStripped.startswith('raise ') or \
           prevLineStripped.startswith('return '):
            return self._decreaseIndent(prevIndent)

        if prevLineStripped and \
           prevLineStripped[-1] in ')]}':
            try:
                foundBlock, foundColumn = self.findBracketBackward(prevNonEmptyBlock,
                                                                   len(prevNonEmptyBlock.text().rstrip()) - 1,
                                                                   prevLineStripped[-1])
            except ValueError:
                pass
            else:
                prevIndent = self._blockIndent(foundBlock)

        return prevIndent
