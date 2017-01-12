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
from utils import (xqt, pushd, wget, mkdir, chdir, build_os, is_64bits,
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

    # Download and compile PCRE.
    pcre_raw_ver = '8.39'
    pcre_ver = 'pcre-' + pcre_raw_ver
    pcre_zip = pcre_ver + '.zip'
    pcre_zip_path = os.path.join(DOWNLOADS, pcre_zip)
    if not isfile(pcre_zip_path):
        # Note: Don't use ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/,
        # because this sometimes hangs during download, causing the build to
        # fail. Instead, use the more reliable SourceForge mirror.
        wget('http://downloads.sourceforge.net/project/pcre/pcre/{}/{}'.
            format(pcre_raw_ver, pcre_zip), pcre_zip_path)
    # See https://sevenzip.osdn.jp/chm/cmdline/commands/extract_full.htm.
    xqt('7z x {} > nul'.format(pcre_zip_path))
    with pushd(pcre_ver):
        mkdir('build')
        chdir('build')
        # Per https://cmake.org/cmake/help/latest/generator/Visual%20Studio%2014%202015.html,
        # add the Win64 string for 64-bit Python.
        use_Win64 = ' Win64' if is_64bits else ''
        xqt('cmake .. -DBUILD_SHARED_LIBS:BOOL=OFF -DPCRE_SUPPORT_UTF:BOOL=ON '
            '-DPCRE_SUPPORT_JIT:BOOL=ON -G "Visual Studio 14 2015{}"'.
            format(use_Win64),
          'cmake --build . --config Release')

    # First, build Python C extensions. Use this instead of
    # ``build_ext`` so that Enki will have an already-installed qutepart,
    # rather than needing to regenrate the command below.
    xqt('python setup.py build_ext --include-dir={}/build '
        '--lib-dir={}/build/Release --force'.format(pcre_ver, pcre_ver))
    # Next, install it along with its dependencies. See comments at
    # ``install_requires`` on why this is necessary.
    xqt('python -m pip install -e .')
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
