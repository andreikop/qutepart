#!/usr/bin/env python

import sys

import sip
sip.setapi('QString', 2)

from qutepart.syntax import SyntaxManager

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:\n\t%s SYNTAX_FILE_NAME' % sys.argv[0]
    else:
        syntax = SyntaxManager().getSyntaxByXmlName(sys.argv[1])
        string = unicode(syntax)
        print string
