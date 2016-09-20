"""Base class for margins
"""


from PyQt5.QtWidgets import QWidget


class MarginBase(QWidget):
    """Base class which each margin should derive from
    """

    def __init__(self, qpart, name, bit_count):
        """qpart: reference to the editor
           name: margin identifier
           bit_count: number of bits to be used by the margin
        """
        QWidget.__init__(self, qpart)
        self._qpart = qpart
        self._name = name
        self._bit_count = bit_count
        self._bitRange = None
        self.__allocateBits()

    def __allocateBits(self):
        """Allocates the bit range depending on the required bit count
        """
        if self._bit_count < 0:
            raise Exception( "A margin cannot request negative number of bits" )
        if self._bit_count == 0:
            return

        # Build a list of occupied ranges
        leftMargins = self._qpart.getMargins(self._qpart.LEFT_MARGINS)
        rightMargins = self._qpart.getMargins(self._qpart.RIGHT_MARGINS)

        occupiedRanges = []
        for margin in leftMargins + rightMargins:
            bitRange = margin.getBitRange()
            if bitRange is not None:
                # pick the right position
                added = False
                for index in range( len( occupiedRanges ) ):
                    r = occupiedRanges[ index ]
                    if bitRange[ 1 ] < r[ 0 ]:
                        occupiedRanges.insert(index, bitRange)
                        added = True
                        break
                if not added:
                    occupiedRanges.append(bitRange)

        vacant = 0
        for r in occupiedRanges:
            if r[ 0 ] - vacant >= self._bit_count:
                self._bitRange = (vacant, vacant + self._bit_count - 1)
                return
            vacant = r[ 1 ] + 1
        # Not allocated, i.e. grab the tail bits
        self._bitRange = (vacant, vacant + self._bit_count - 1)

    def getName(self):
        """Provides the margin identifier
        """
        return self._name

    def getBitRange(self):
        """None or inclusive bits used pair,
           e.g. (2,4) => 3 bits used 2nd, 3rd and 4th
        """
        return self._bitRange

    def setBlockValue(self, block, value):
        """Sets the required value to the block without damaging the other bits
        """
        if self._bit_count == 0:
            raise Exception( "The margin '" + self._name +
                             "' did not allocate any bits for the values")
        if value < 0:
            raise Exception( "The margin '" + self._name +
                             "' must be a positive integer"  )

        if value >= 2 ** self._bit_count:
            raise Exception( "The margin '" + self._name +
                             "' value exceeds the allocated bit range" )

        current = block.userState()
        value <<= self._bitRange[ 0 ]
        if current in [ 0, -1 ]:
            block.setUserState(value)
        else:
            block.setUserState(current | value)


    def getBlockValue(self, block):
        """Provides the previously set block value respecting the bits range.
           0 value and not marked block are treated the same way and 0 is
           provided.
        """
        if self._bit_count == 0:
            raise Exception( "The margin '" + self._name +
                             "' did not allocate any bits for the values")
        val = block.userState()
        if val in [ 0, -1 ]:
            return 0

        # Shift the value to the right
        val >>= self._bitRange[ 0 ]

        # Apply the mask to the value
        mask = 2 ** self._bit_count - 1
        val &= mask
        return val

    def hide(self):
        """Override the QWidget::hide() method to properly recalculate the
           editor viewport.
        """
        if not self.isHidden():
            QWidget.hide(self)
            self._qpart.updateViewport()

    def show(self):
        """Override the QWidget::show() method to properly recalculate the
           editor viewport.
        """
        if self.isHidden():
            QWidget.show()
            self._qpart.updateViewport()

    def setVisible(self, val):
        """Override the QWidget::setVisible(bool) method to properly
           recalculate the editor viewport.
        """
        if val != self.isVisible():
            if val:
                self.show()
            else:
                self.hide()

    # Convenience methods

    def clear(self):
        """Convenience method to reset all the block values to 0
        """
        if self._bit_count == 0:
            return
        for block in qutepart.iterateBlocksFrom(self._qpart.document().begin()):
            if self.getBlockValue(block):
                self.setBlockValue(block, 0)

    # Methods for 1-bit margins
    def isBlockMarked(self, block):
        return self.getBlockValue(block) != 0
    def toggleBlockMark(self, block):
        self.setBlockValue(block, 1 if self.isBlockMarked(block) else 0)



if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    class MockMargin:
        def __init__(s, l, r):
            s.br = (l, r)
        def getBitRange(s):
            return s.br

    class MockQPart(QWidget):
        LEFT_MARGINS = 0
        RIGHT_MARGINS = 1
        def __init__(s):
            QWidget.__init__(s, None)
            s.left = [ MockMargin(1, 3), MockMargin(7, 8) ]
            s.right = [ MockMargin(4, 4) ]
        def getMargins(s, t):
            return s.left if t == s.LEFT_MARGINS else s.right

    q = MockQPart()
    m = MarginBase(q, "test margin", 1)
    print(m.getName())
    print(m.getBitRange())

    m = MarginBase(q, "test margin", 2)
    print(m.getName())
    print(m.getBitRange())

