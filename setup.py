#!/usr/bin/env python

from distutils.core import setup, Extension

packages=['qutepart']

package_data={'qutepart' : ['syntax/*.xml',
                            'syntax/syntax_db.json']
             }

extension = Extension('qutepart.cParser',
                      sources = ['qutepart/parsermodule.c'],
                      libraries = ['pcre'])


setup (name = 'qutepart',
       version = '1.0',
       description = 'Syntax highlighter based on katepart XML files',
       packages = packages,
       package_data = package_data,
       ext_modules = [extension])
