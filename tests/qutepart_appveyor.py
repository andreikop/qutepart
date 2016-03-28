# ************************************************
# appveyor.py - Script to run CI tests on Appveyor
# ************************************************
#
# Standard library
# ----------------
import os
import subprocess
from os.path import isfile
#
# Local application imports
# -------------------------
from ci_utils import xqt, pushd, wget, mkdir, chdir, build_os, system_identify
#
# Windows
# =======
def install():
    system_identify()

    # This was based on ideas from https://github.com/pyinstaller/pyinstaller/blob/develop/appveyor.yml.

    # Download and install PyQt5. Only download if we don't have a cached copy
    # available.
    install_PyQt5 = 'install-PyQt5.exe'
    if not isfile(install_PyQt5):
        wget('http://downloads.sourceforge.net/project/pyqt/PyQt5/PyQt-5.5.1/PyQt5-5.5.1-gpl-Py3.4-Qt5.5.1-x32.exe?r=&ts=1458769604&use_mirror=heanet',
             install_PyQt5)
    # See https://github.com/appveyor/ci/issues/363#issuecomment-148915001.
    xqt('REG ADD HKCU\\Software\\Python\\PythonCore\\3.4\\InstallPath /f /ve '
        '/t REG_SZ /d C:\\Python34',
      install_PyQt5 + ' /S')

    # Download and compile PCRE.
    pcre_ver = 'pcre-8.37'
    pcre_zip = pcre_ver + '.zip'
    if not isfile(pcre_zip):
        wget('ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/' +
             pcre_zip)
    # See https://sevenzip.osdn.jp/chm/cmdline/commands/extract_full.htm.
    xqt('7z x {} > nul'.format(pcre_zip))
    with pushd(pcre_ver):
        mkdir('build')
        chdir('build')
        xqt('cmake .. -DBUILD_SHARED_LIBS:BOOL=OFF -DPCRE_SUPPORT_UTF:BOOL=ON '
            '-DPCRE_SUPPORT_JIT:BOOL=ON -G "Visual Studio 10 2010"',
          'cmake --build . --config Release')

    # Build Python C extensions.
    xqt('python setup.py build_ext --include-dir={}/build '
        '--lib-dir={}/build/Release --force'.format(pcre_ver, pcre_ver))

    # Run the tests.
    chdir('tests')
    xqt('python run_all.py')

if __name__ == '__main__':
    assert build_os == 'Windows'
    install()
