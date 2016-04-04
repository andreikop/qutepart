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
# OS_Specific
# ===========
# This class dispatches its methods to their OS-specific variants. For example, when ``build_os = 'Linux'``, ``o = OS_Specific(); o.pcre()`` invokes ``pcre_Linux``.
class OS_Specific:
    def __getattr__(self, name):
        return self.__getattribute__(name + '_' + build_os)

    # _`qt5_Linux`: Note: the Qt version here must agree with the version used in pyqt5_configure_Linux_ and be compatible with pyqt_ver_.
    def qt5_Linux(self):
        # There are two Qt version strings here -- keep them in sync. See https://launchpad.net/~beineri/+archive/ubuntu/opt-qt551-trusty.
        xqt('sudo add-apt-repository -y ppa:beineri/opt-qt551',
          'sudo apt-get update',
          'sudo apt-get install -y qt55base')
    # _`qt5_OS_X`: Note: the Qt version here must agree with the version used in pyqt5_configure_OS_X_ and be compatible with pyqt_ver_.
    def qt5_OS_X(self):
        # Note: ``brew linkapps qt55`` doesn't link qmake, so it's omitted.
        xqt('brew install qt55')

    # See http://pyqt.sourceforge.net/Docs/PyQt5/installation.html#configuring-pyqt5.
    configure_options = ' -c --confirm-license --no-designer-plugin'
    # _`pyqt5_configure_Linux`: See also qt5_Linux_ for other places the Qt version must agree.
    def pyqt5_configure_Linux(self):
        # The environment variables set by the script are lost when the shell exits. So, run configure.py in the same bash instance.
        xqt('source /opt/qt55/bin/qt55-env.sh; python configure.py' + self.configure_options)
    # _`pyqt5_configure_OS_X`: See also qt5_OS_X_ for other places the Qt version must agree.
    def pyqt5_configure_OS_X(self):
        # The path to qmake can be obtained by looking at the output of ``brew install qt55``.
        xqt('python configure.py --qmake=/usr/local/Cellar/qt55/5.5.1/bin/qmake' + self.configure_options)

    def pcre_Linux(self):
        xqt('sudo apt-get install -y libpcre3-dev')
    def pcre_OS_X(self):
        xqt('brew install pcre')
#
# install
# =======
def install():
    # Based on ideas from https://github.com/harvimt/quamash/blob/master/.travis.yml
    system_identify()
    oss = OS_Specific()
    xqt(
      # Cached Downloads
      'sudo mkdir -p /downloads',
      'sudo chmod a+rw /downloads')
    sip_ver = 'sip-4.17'
    if not isfile('/downloads/sip.tar.gz'):
        wget('http://sourceforge.net/projects/pyqt/files/sip/{}/{}'.format(sip_ver, _gz(sip_ver)), '/downloads/sip.tar.gz')
    # _`pyqt_ver`: Select a PyQt version. See also qt5_Linux_ and qt5_OS_X_.
    pyqt_ver = '5.5.1'
    pyqt_gpl_ver = 'PyQt-gpl-' + pyqt_ver
    if not isfile('/downloads/pyqt5.tar.gz'):
        wget('http://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-{}/{}'.format(pyqt_ver, _gz(pyqt_gpl_ver)), '/downloads/pyqt5.tar.gz')
    # Builds
    xqt('sudo mkdir -p /builds',
      'sudo chmod a+rw /builds')

    # Qt5
    oss.qt5()

    # SIP. With Linux or OS_X, don't use the package manager to install these, since they're installed for the system python, not the pyenv version we're testing with.
    with pushd('/builds'):
        xqt('tar xzf /downloads/sip.tar.gz --keep-newer-files')
        chdir(sip_ver)
        xqt('python configure.py',
          'make',
          'sudo make install')

    # PyQt5
    with pushd('/builds'):
        xqt('tar xzf /downloads/pyqt5.tar.gz --keep-newer-files')
        chdir(pyqt_gpl_ver)
        oss.pyqt5_configure()
        xqt('make',
          'sudo make install')

    # PCRE
    oss.pcre()

    # Qutepart
    if build_os == 'Linux':
        _set_display()
        xqt('sh -e /etc/init.d/xvfb start')
    xqt('python setup.py build_ext')

def _gz(s):
    return s + '.tar.gz'

def _set_display():
    # Avoid the error ``QXcbConnection: Could not connect to display``. The
    # DISPLAY must be set before running xvfb.
    os.environ['DISPLAY'] = ':99.0'
#
# test
# ====
def test():
    if build_os == 'Linux':
        _set_display()
    chdir('tests')
    # Now run the tests.
    xqt('python run_all.py')
#
# main
# ====
# Parse given arguments, then run the commands they select.
def main():
    assert build_os == 'Linux' or build_os == 'OS_X'
    assert len(sys.argv) == 2
    if sys.argv[1] == 'install':
        install()
    elif sys.argv[1] == 'script':
        test()
    else:
        raise RuntimeError('Unknown argument ' + sys.argv[1])

if __name__ == '__main__':
    main()
