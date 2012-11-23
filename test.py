#!/usr/bin/env python

import sys

sys.path.append('./build/lib.linux-i686-2.6/qutepart')

from cParser import *

p = Parser(None, None, None, None)
c = Context(p, "test context")
c.setValues(1, 'a format', c, c, 5, 6)

p.setContexts([c], c)

print p.parseBlock(u"thedata", u"thetext")

