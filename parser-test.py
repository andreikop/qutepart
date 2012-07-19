#!/usr/bin/env python

import sys

import sip
sip.setapi('QString', 2)

from qutepart.Syntax import Syntax

if __name__ == '__main__':
    if len(sys.argv) > 1:
        syntax = Syntax(sys.argv[1])
    else:
        syntax = Syntax('debianchangelog.xml')
    print syntax
