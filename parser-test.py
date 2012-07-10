#!/usr/bin/env python

import sys

import sip
sip.setapi('QString', 2)


from qutepart.Syntax import Syntax

if __name__ == '__main__':
    syntax = Syntax('debianchangelog.xml')
    print syntax
