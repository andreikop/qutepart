#!/usr/bin/env python

import sys

import sip
sip.setapi('QString', 2)

from qutepart.syntax_manager import SyntaxManager

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:\n\t%s SYNTAX_FILE_NAME' % sys.argv[0]
    else:
        print SyntaxManager().getSyntaxByXmlName(sys.argv[1])
