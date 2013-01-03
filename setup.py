#!/usr/bin/env python

from distutils.core import setup, Extension

packages=['qutepart', 'qutepart/syntax']

package_data={'qutepart/syntax' : ['data/*.xml',
                                   'data/syntax_db.json']
             }

extension = Extension('qutepart.syntax.cParser',
                      sources = ['qutepart/syntax/cParser.c'],
                      libraries = ['pcre'])
#extension.extra_compile_args = ['-O0', '-g']

setup (name = 'qutepart',
       version = '1.0',
       description = 'Code editor component for PyQt and PySide',
       packages = packages,
       package_data = package_data,
       ext_modules = [extension])
