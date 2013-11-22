#!/usr/bin/env python

import sys
import os

from distutils.core import setup, Extension
import distutils.ccompiler
import distutils.sysconfig

import qutepart


def parse_arg_list(param_start):
    """Exctract values like --libdir=bla/bla/bla
    param_start must be '--libdir='
    """
    values = [arg[len(param_start):] \
                for arg in sys.argv \
                if arg.startswith(param_start)]
    
    # remove recognized arguments from the sys.argv
    otherArgs = [arg \
                    for arg in sys.argv \
                    if not arg.startswith(param_start)]
    sys.argv = otherArgs
    
    return values


packages=['qutepart', 'qutepart/syntax', 'qutepart/indenter']

package_data={'qutepart' : ['icons/*.png'],
              'qutepart/syntax' : ['data/xml/*.xml',
                                   'data/syntax_db.json']
             }


include_dirs = parse_arg_list('--include-dir=')
if not include_dirs:
    include_dirs = ['/usr/include', '/usr/local/include', '/opt/local/include']

library_dirs = parse_arg_list('--lib-dir=')
if not library_dirs:
    library_dirs = ['/usr/lib', '/usr/local/lib', '/opt/local/lib']



extension = Extension('qutepart.syntax.cParser',
                      sources = ['qutepart/syntax/cParser.c'],
                      libraries = ['pcre'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs)


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
        print "Try to install python-dev package"
        print "If not standard directories are used, pass parameters"
        print "\tpython setup.py install --lib-dir=/my/local/lib --include-dir=/my/local/include"
        print "--lib-dir= and --include-dir= may be used multiple times"
        return False
    
    if not compiler.has_function('pcre_version',
                                 includes = ['pcre.h'],
                                 libraries = ['pcre'],
                                 include_dirs=include_dirs,
                                 library_dirs=include_dirs):
        print "Failed to find pcre library."
        print "Try to install libpcre{version}-dev package, or go to http://pcre.org"
        print "If not standard directories are used, pass parameters:"
        print "\tpython setup.py install --lib-dir=/my/local/lib --include-dir=/my/local/include"
        print "--lib-dir= and --include-dir= may be used multiple times"
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
