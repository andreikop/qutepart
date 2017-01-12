# *******************************************
# qutepart_travis.py - Run CI tests on Travis
# *******************************************
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
import sys
import os
#
# Third-party imports
# -------------------
# None.
#
# Local application imports
# -------------------------
from utils import (xqt, pushd, chdir, build_os, system_identify, wget,
                   command_line_invoke, OS_Dispatcher, isfile)
#
# Travis_Dispatcher
# =================
# This provides OS-specific variants of needed installs.
class Travis_Dispatcher(OS_Dispatcher):
#
# pcre
# ----
    def pcre_Linux(self):
        # Travis Linux notes: this fixed the error::
        #
        #   This application failed to start because it could not find or load the Qt platform plugin "xcb"
        #   in "".
        #   Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, xcb.
        #
        # To help debug, run ``QT_DEBUG_PLUGINS=1 python run_all.py``, which 
        # produced (along with lots of other output)::
        #
        #   Cannot load library /home/travis/virtualenv/python3.5.2/lib/python3.5/site-packages/PyQt5/Qt/plugins/platforms/libqxcb.so: (libEGL.so.1: cannot open shared object file: No such file or directory)
        #
        # Adding the ``libegl1-mesa`` package fixes this.
        xqt('sudo apt-get install -y libpcre3-dev libegl1-mesa')
    def pcre_OS_X(self):
        xqt('brew install pcre')
#
# install
# =======
def install(should_identify=True):
    # Based on ideas from https://github.com/harvimt/quamash/blob/master/.travis.yml
    if should_identify:
        system_identify()
    td = Travis_Dispatcher()

    # PCRE
    td.pcre()

    # Qutepart
    if build_os == 'Linux':
        set_display()
        xqt('sh -e /etc/init.d/xvfb start')
    # Install, which also builds Python C extensions. Use this instead of
    # ``build_ext`` so that Enki will have an already-installed qutepart,
    # rather than needing to regenrate the command below.
    xqt('python -m pip install -e .')
#
# Supporting utilities
# --------------------
# Avoid the error ``QXcbConnection: Could not connect to display``. The
# DISPLAY must be set before running xvfb.
def set_display():
    if build_os == 'Linux':
        os.environ['DISPLAY'] = ':99.0'
#
# test
# ====
def test():
    set_display()
    chdir('tests')
    # Now run the tests.
    xqt('python run_all.py')
#
# main
# ====
def main():
    assert build_os == 'Linux' or build_os == 'OS_X'
    command_line_invoke(install, test)

if __name__ == '__main__':
    main()
