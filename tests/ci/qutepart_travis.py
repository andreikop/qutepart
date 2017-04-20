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
import os
#
# Third-party imports
# -------------------
# None.
#
# Local application imports
# -------------------------
from utils import (xqt, chdir, build_os, system_identify,
                   command_line_invoke, OS_Dispatcher)
#
# Travis_Dispatcher
# =================
# This provides OS-specific variants of needed installs.
class Travis_Dispatcher(OS_Dispatcher):
    def install_Linux(self):
        # Travis Linux notes: adding the ``libegl1-mesa`` package fixes the error::
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
        # Travis Linux notes: adding the test repo then installing ``libstdc++6`` fixes ``ImportError: /usr/lib/x86_64-linux-gnu/libstdc++.so.6: version `GLIBCXX_3.4.18' not found (required by /home/travis/virtualenv/python3.5.2/lib/python3.5/site-packages/PyQt5/Qt/lib/libQt5WebEngineCore.so.5)``.
        xqt('sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test',
            'sudo apt-get update',
            'sudo apt-get install -y libpcre3-dev libegl1-mesa libstdc++6')

        set_display()
        xqt('sh -e /etc/init.d/xvfb start')

    def install_OS_X(self):
        # Nothing needed. PCRE is installed as a part of ``osx_python_install.sh``.
        pass

    def install_Windows(self):
        # A dummy name to make Enki installs easier. All the real work is done in ``qutepart_appveyor.py``.
        pass
#
# install
# =======
def install():
    system_identify()
    Travis_Dispatcher().install()

    # Install, which also builds Python C extensions. Use this instead of
    # ``build_ext`` so that Enki will have an already-installed qutepart,
    # rather than needing to regenerate the command below.
    xqt('python -m pip install -e .')
#
# Supporting utilities
# --------------------
# Avoid the error ``QXcbConnection: Could not connect to display``. The
# DISPLAY must be set before running xvfb.
def set_display():
    os.environ['DISPLAY'] = ':99.0'
#
# test
# ====
def test():
    if build_os == 'Linux':
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
