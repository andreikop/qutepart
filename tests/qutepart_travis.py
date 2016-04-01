# **********************************
# travis.py - Run CI tests on Travis
# **********************************
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
import sys
import os
from os.path import isfile
#
# Local application imports
# -------------------------
from ci_utils import xqt, pushd, chdir, build_os, system_identify, wget
#
# Linux
# =====
def install():
    # Based on ideas from https://github.com/harvimt/quamash/blob/master/.travis.yml
    system_identify()
    xqt(
      # Cached Downloads
      'sudo mkdir -p /downloads',
      'sudo chmod a+rw /downloads')
    sip_ver = 'sip-4.16.5'
    sip_gz = sip_ver + '.tar.gz'
    if not isfile('/downloads/sip.tar.gz'):
        wget('http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.5/sip-4.16.5.tar.gz', '/downloads/sip.tar.gz')
    if not isfile('/downloads/pyqt5.tar.gz'):
        wget('http://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.4/PyQt-gpl-5.4.tar.gz', '/downloads/pyqt5.tar.gz')
    xqt('echo "6d01ea966a53e4c7ae5c5e48c40e49e5  /downloads/sip.tar.gz" | md5sum -c -',
      'echo "7f2eb79eaf3d7e5e7df5a4e9c8c9340e  /downloads/pyqt5.tar.gz" | md5sum -c -',
      # Builds
      'sudo mkdir -p /builds',
      'sudo chmod a+rw /builds')

    # Qt5
    xqt('sudo add-apt-repository -y ppa:beineri/opt-qt542',
      'sudo apt-get update',
      'sudo apt-get install -y qt54base')
    # SIP
    with pushd('/builds'):
        xqt('tar xzf /downloads/sip.tar.gz --keep-newer-files')
        chdir('sip-4.16.5')
        xqt('python configure.py',
          'make',
          'sudo make install')
    # PyQt5
    with pushd('/builds'):
        xqt('tar xzf /downloads/pyqt5.tar.gz --keep-newer-files')
        chdir('PyQt-gpl-5.4')
        # Use a helper script to set up for Qt 5.4, then compile PyQt5.
        with open('pyqt_configure.sh', 'w') as f:
            f.write('#!/bin/bash\n'
                    'source /opt/qt54/bin/qt54-env.sh\n'
                    'python configure.py -c --confirm-license --no-designer-plugin')
        xqt('bash pyqt_configure.sh',
          'make',
          'sudo make install')

    # Qutepart.
    # Avoid the error ``QXcbConnection: Could not connect to display``. The
    # DISPLAY must be set before running xvfb.
    os.environ['DISPLAY'] = ':99.0'
    xqt('sh -e /etc/init.d/xvfb start')
    xqt('python setup.py build_ext')

def test():
    os.environ['DISPLAY'] = ':99.0'
    chdir('tests')
    # Now run the tests.
    xqt('python run_all.py')
#
# Main code
# =========
# _`main`: Parse given arguments, then run the given commands.
def main():
    assert build_os == 'Linux'
    assert len(sys.argv) == 2
    if sys.argv[1] == 'install':
        install()
    elif sys.argv[1] == 'script':
        test()
    else:
        raise RuntimeError('Unknown argument ' + sys.argv[1])

if __name__ == '__main__':
    main()
