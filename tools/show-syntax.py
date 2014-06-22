#!/usr/bin/env python3

import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')

import sip
sip.setapi('QString', 2)

from qutepart.syntax import SyntaxManager

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:\n\t%s SYNTAX_FILE_NAME' % sys.argv[0])
    else:
        syntax = SyntaxManager().getSyntax(xmlFileName = sys.argv[1])
        print(str(syntax))
