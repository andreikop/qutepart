"""Module indentation for block
"""

class Indenter:
    """Class automatically computes indentation for lines
    """
    def __init__(self, qpart):
        self._qpart = qpart
    
    @staticmethod
    def _prevBlockIndent(block):
        prevBlock = block.previous()
        
        while prevBlock.isValid() and not prevBlock.text():  # try to find non-empty block
            prevBlock = prevBlock.previous()
        
        if prevBlock.isValid():
            text = prevBlock.text()
            spaceAtStart = text[:len(text) - len(text.lstrip())]
            return spaceAtStart
        else:
            return ''

    def computeIndent(self, block):
        """Compute indent for block
        """
        prevLineIndent = self._prevBlockIndent(block)
        
        return prevLineIndent