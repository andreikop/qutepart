# *********************************************************
# qutepart_appveyor.py - Script to run CI tests on Appveyor
# *********************************************************
#
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
from utils import (xqt, pushd, wget, mkdir, chdir, build_os,
                   system_identify, command_line_invoke, isfile, isdir)
#
# install
# =======
DOWNLOADS = '\\downloads'
def install(should_identify=True):
    if should_identify:
        system_identify()

    # Create a place to store downloads.
    if not isdir(DOWNLOADS):
        mkdir(DOWNLOADS)

    # Download and install PyQt5. Only download if we don't have a cached copy
    # available.
    install_PyQt5 = os.path.join(DOWNLOADS, 'install-PyQt5.exe')
    if not isfile(install_PyQt5):
        wget('http://downloads.sourceforge.net/project/pyqt/PyQt5/PyQt-5.5.1/'
             'PyQt5-5.5.1-gpl-Py3.4-Qt5.5.1-x32.exe',
              install_PyQt5)
    # See https://github.com/appveyor/ci/issues/363#issuecomment-148915001.
    xqt('REG ADD HKCU\\Software\\Python\\PythonCore\\3.4\\InstallPath /f /ve '
        '/t REG_SZ /d C:\\Python34',
      install_PyQt5 + ' /S')

    # Download and compile PCRE.
    pcre_ver = 'pcre-8.38'
    pcre_zip = pcre_ver + '.zip'
    pcre_zip_path = os.path.join(DOWNLOADS, pcre_zip)
    if not isfile(pcre_zip_path):
        # Note: Don't use ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/,
        # because this sometimes hangs during download, causing the build to
        # fail. Instead, use the more reliable SourceForge mirror.
        wget('http://downloads.sourceforge.net/project/pcre/pcre/8.38/' +
             pcre_zip, pcre_zip_path)
    # See https://sevenzip.osdn.jp/chm/cmdline/commands/extract_full.htm.
    xqt('7z x {} > nul'.format(pcre_zip_path))
    with pushd(pcre_ver):
        mkdir('build')
        chdir('build')
        xqt('cmake .. -DBUILD_SHARED_LIBS:BOOL=OFF -DPCRE_SUPPORT_UTF:BOOL=ON '
            '-DPCRE_SUPPORT_JIT:BOOL=ON -G "Visual Studio 10 2010"',
          'cmake --build . --config Release')

    # Install, which also builds Python C extensions. Use this instead of
    # ``build_ext`` so that Enki will have an already-installed qutepart,
    # rather than needing to regenrate the command below.
    xqt('python setup.py install --include-dir={}/build '
        '--lib-dir={}/build/Release --force'.format(pcre_ver, pcre_ver))
#
# test
# ====
# Run the tests.
def test():
    chdir('tests')
    xqt('python run_all.py')
#
# main
# ====
def main():
    assert build_os == 'Windows'
    command_line_invoke(install, test)

if __name__ == '__main__':
    main()
