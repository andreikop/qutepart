# ***************************************************************
# ci_utils.py - Utilities supporting continuous integration tests
# ***************************************************************
# Originally, there were full ``.travis.yml`` and ``appveyor.yml`` scripts.
# This becomes awkward:
#
# #. Any conditional logic means ugly syntax. It's also not portable between
#    Windows and Linux/Mac.
# #. There's no way to re-use code between the two CI systems.
# #. There's no way to re-use code for Enki, which needs to build Qutepart
#    first.
#
# Hence, the use of Python as a more robust script approach for CI testing.
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
from subprocess import check_call
import sys
import os
import platform
#
# Third-party imports
# -------------------
import wget as wget_
#
# OS detection
# ============
if sys.platform.startswith('win'):
    build_os = 'Windows'
elif sys.platform.startswith('linux'):
    build_os = 'Linux'
elif sys.platform == 'darwin':
    build_os = 'OS X'
else:
    # Unsupported platform.
    assert False
#
# Support code
# ============
# _`xqt`: Provide a simple way to execute a system command.
def xqt(
  # Commands to run. For example, ``'foo -param firstArg secondArg', 'bar |
  # grep alpha'``.
  *cmds,
  # Optional keyword arguments to pass on to `subprocess.check_call <https://docs.python.org/3/library/subprocess.html#subprocess.check_call>`_.
  **kwargs):

    # Although https://docs.python.org/3/library/subprocess.html#subprocess.Popen
    # states, "The only time you need to specify ``shell=True`` on Windows is
    # when the command you wish to execute is built into the shell (e.g.
    # **dir** or **copy**). You do not need ``shell=True`` to run a batch file
    # or console-based executable.", use ``shell=True`` to both allow shell
    # commands and to support simple redirection (such as ``blah > nul``,
    # instead of passing stdout=subprocess.DEVNULL to ``check_call``).
    for _ in cmds:
        print(_)
        # Per http://stackoverflow.com/questions/15931526/why-subprocess-stdout-to-a-file-is-written-out-of-order,
        # the ``check_call`` below will flush stdout and stderr, causing all
        # the subprocess output to appear first, followed by all the Python
        # output (such as the print statement above).
        sys.stdout.flush()
        sys.stderr.flush()
        check_call(_, shell=True, **kwargs)

# A decorator for pushd.
class pushd:
    def __init__(self,
      # The path to change to upon entering the context manager.
      path):

        self.path = path

    def __enter__(self):
        print('pushd {}'.format(self.path))
        self.cwd = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, type_, value, traceback):
        print('popd - returning to {}.'.format(self.cwd))
        os.chdir(self.cwd)
        return False

# Report what we know about the system we're running on.
def system_identify():
    if build_os == 'Windows':
        release, version, csd, ptype = platform.win32_ver()
        plat_str = 'release {}, version {}, service pack {}, type {}'.format(
          release, version, csd, ptype)
    elif build_os == 'Linux':
        # Avoid the deprecated platform.dist().
        lib, version = platform.libc_ver()
        plat_str = '{} version {}'.format(lib, version)
    elif build_os == 'OS X':
        release, (version, dev_stage, non_release_version), machine = \
          platform.mac_ver()
        plat_str = ('release {}, dev stage {}, non-relase version {}, machine '
          '{}'.format(release, version, dev_stage, non_release_version,
                      machine))
    system, release, version = platform.system_alias(platform.system(),
      platform.release(), platform.version())
    print('Python {}, OS {}, platform {} {} - {}'.format(sys.version, os.name,
      system, release, version, plat_str))

def wget(src, dst=None):
    print('wget {} {}'.format(src, dst if dst else ''))
    wget_.download(src, dst)

def chdir(path):
    print('cd ' + path)
    os.chdir(path)

def mkdir(path):
    print('mkdir ' + path)
    os.mkdir(path)
