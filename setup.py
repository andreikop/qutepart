#!/usr/bin/env python

from distutils.core import setup, Extension

packages=['qutepart']

extension = Extension('qutepart.cParser', sources = ['qutepart/parsermodule.c'])

setup (name = 'qutepart',
       version = '1.0',
       description = 'Syntax highlighter based on katepart XML files',
       packages = packages,
       ext_modules = [extension])