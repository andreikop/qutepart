import re

from qutepart.indenter.base import IndentAlgBase

class IndentAlgLisp(IndentAlgBase):
    TRIGGER_CHARACTERS = ";"

    def computeSmartIndent(self, block, ch):
        """special rules: ;;; -> indent 0
                          ;;  -> align with next line, if possible
                          ;   -> usually on the same line as code -> ignore
        """
        if re.search(r'^\s*;;;', block.text()):
            return ''
        elif re.search(r'^\s*;;', block.text()):
            #try to align with the next line
            nextBlock = self._nextNonEmptyBlock(block)
            if nextBlock.isValid():
                return self._blockIndent(nextBlock)

        try:
            foundBlock, foundColumn = self.findBracketBackward(block, 0, '(')
        except ValueError:
            return ''
        else:
            return self._increaseIndent(self._blockIndent(foundBlock))
