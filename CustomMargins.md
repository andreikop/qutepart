# Custom Margins

Qutepart supports custom margins on the left hand side of the editor pane.
Each margin has a unique string identifier and two margins are instantiated at
the time the quitepart is created:

* Line numbers margin
* Marks margin which can display pylint messages and handles bookmarks

The line numbers margin uses the "line_numbers" identifier and the marks margin
uses the "mark_area" identifier.


## Interface

### Getting a list of margins

```python
# Returns a list of the current margins
qpart.getMargins()
```

### Looking up for a margin

```python
# Returns a reference to the line numbers margin or None if not found
margin = qpart.getMargin("line_numbers")
```

### Removing a margin

```python
if qpart.delMargin("mark_area"):
    print("Mark area margin has been removed")
else:
    print("Mark area margin is not found")
```

### Hiding/showing margins

```python
margin = qpart.getMargin("line_numbers")
if margin:
    margin.hide()
    # later on the margin can be shown again: margin.show()
```


### Adding margin

```python
margin1 = MyMargin1(qpart, ...)
margin2 = MyMargin2(qpart, ...)

# will add the margin as the most right
qpart.addMargin(margin1)

# will add the margin as the most left
# the second argument is a list index to be inserted at
qpart.addMargin(margin2, 0)
```


## Custom margins

### Overview

All margins must derive from the QWidget and MarginBase classes. Due to some
PyQT5 implementation details there is no good way to implement the hierarchy
nicely so a workaround has been developed.

The custom margin code may look as follows:

```python
class MyMargin(QWidget):
    """Custom margin
    """
    def __init__(self, parent)
        QWidget.__init__(self, parent)

        # Here is a hack to add MarginBase into a list of base classes
        # See qutepart/sideareas.py for details
        extend_instance(self, MarginBase)

        # Now the MarginBase constructor can be called
        MarginBase.__init__(self, parent, "my margin ID", 2)

    def width(self):
        # The width of the margin in pixels. The hight will be calculated
        # automatically as the height of the editor widget
        return 32
```

After that the margin could be added to the editor with the addMargin(...)
call as described above.


### Bits for marking blocks

The example above has the following initialization of the MarginBase:

```python
MarginBase.__init__(self, parent, "my margin ID", 2)
```

The last argument is a number of bits the margin wants to reserve for marking
blocks. The QPlainTextEditor class (a base for qutepart) supports an integer
value associated with each block. That value could be used to store some
user information. In case of many margins it is possible that a few of them
need to mark blocks, e.g. if a block is bookmarked. So to avoid conflicts
in values stored in blocks each margin has to declare how many bits it needs and
the bits are reserved for the margin automatically respecting what has already
been reserved for the others. If a margin does not use any bits it should
have 0 in the MarginBase.__init__(...) call.

Having some bits reserved a margin should not manipulate the block values directly.
Instead it should used a couple of members provided by the MarginBase class:

* setBlockValue(block, value) - checks the value range, do the appropriate
  shift and sets the block value without damaging the other margin values
* getBlockValue(block) - retrieves the block value and does the appropriate
  shift and masking

So regardless of what the exact bits are allocated for a margin the following
code will work:

```python
class MyMargin(QWidget):
    ...
    def someMethod(self, block):
        self.setBlockValue(block, 3)
        if self.getBlockValue(block) != 3:
            raise Exception("Cannot happen")
```

