#!/usr/bin/env python

import sys
import os

from distutils.core import setup, Extension
import distutils.ccompiler
import distutils.sysconfig

import qutepart

packages=['qutepart', 'qutepart/syntax', 'qutepart/indenter']

package_data={'qutepart' : ['icons/*.png'],
              'qutepart/syntax' : ['data/xml/*.xml',
                                   'data/syntax_db.json']
             }

pcre_include_dirs = [os.environ['PCRE_INCLUDE_DIR']] if 'PCRE_INCLUDE_DIR' in os.environ else []
pcre_library_dirs = [os.environ['PCRE_LIBRARY_DIR']] if 'PCRE_LIBRARY_DIR' in os.environ else []

if sys.platform == 'darwin':
    if not pcre_include_dirs and \
       not pcre_library_dirs:
        # default locations for mac ports
        pcre_include_dirs.append('/opt/local/include')
        pcre_library_dirs.append('/opt/local/lib')


extension = Extension('qutepart.syntax.cParser',
                      sources = ['qutepart/syntax/cParser.c'],
                      libraries = ['pcre'],
                      include_dirs=pcre_include_dirs,
                      library_dirs=pcre_library_dirs)


def _checkDependencies():
    compiler = distutils.ccompiler.new_compiler()
    """check if function without parameters from stdlib can be called
    There should be better way to check, if C compiler is installed
    """
    if not compiler.has_function('rand', includes = ['stdlib.h']):
        print "It seems like C compiler is not installed or not operable."
        return False
    
    if not compiler.has_function('rand',
                                 includes = ['stdlib.h', 'Python.h'],
                                 include_dirs=[distutils.sysconfig.get_python_inc()]):
        print "Failed to find Python headers."
        print "\tTry to install python-dev package"
        print "\tIf not standard directories are used, set CFLAGS and LDFLAGS environment variables"
        return False
    
    if not compiler.has_function('pcre_version',
                                 includes = ['pcre.h'],
                                 libraries = ['pcre'],
                                 include_dirs=pcre_include_dirs,
                                 library_dirs=pcre_library_dirs):
        print "Failed to find pcre library."
        print "\tTry to install libpcre{version}-dev package, or go to http://pcre.org"
        print "\tIf not standard directories are used, set environment variables:"
        print "\t\tPCRE_INCLUDE_DIR - location of pcre.h header"
        print "\t\tPCRE_LIBRARY_DIR - location of libpcre.a library"
        return False
    
    return True


if 'install' in sys.argv or 'build' in sys.argv or 'build_ext' in sys.argv:
    if not '--force' in sys.argv and not '--help' in sys.argv:
        if not _checkDependencies():
            sys.exit(-1)


setup (name='qutepart',
       version='%s.%s.%s' % qutepart.VERSION,
       description='Code editor component for PyQt and PySide',
       author='Andrei Kopats',
       author_email='hlamer@tut.by',
       url='https://github.com/hlamer/qutepart',
       packages = packages,
       package_data = package_data,
       ext_modules = [extension])
