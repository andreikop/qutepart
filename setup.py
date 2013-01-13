#!/usr/bin/env python

import sys

from distutils.core import setup, Extension
import distutils.ccompiler

packages=['qutepart', 'qutepart/syntax']

package_data={'qutepart/syntax' : ['data/*.xml',
                                   'data/syntax_db.json']
             }

extension = Extension('qutepart.syntax.cParser',
                      sources = ['qutepart/syntax/cParser.c'],
                      libraries = ['pcre'])


def _checkDependencies():
    compiler = distutils.ccompiler.new_compiler()
    if not compiler.has_function('pcre_version', includes = ['pcre.h'], libraries = ['pcre']):
        print "Failed to find pcre library."
        print "\tTry to install libpcre{version}-dev package, or go to http://pcre.org"
        print "\tIf not standard directories are used, set CFLAGS and LDFLAGS environment variables"
        return False
    
    return True


if 'install' in sys.argv or 'build' in sys.argv or 'build_ext' in sys.argv:
    if not '--force' in sys.argv and not '--help' in sys.argv:
        if not _checkDependencies():
            sys.exit(-1)


setup (name = 'qutepart',
       version = '1.0',
       description = 'Code editor component for PyQt and PySide',
       packages = packages,
       package_data = package_data,
       ext_modules = [extension])
