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
import os.path
import platform
from zipfile import ZipFile
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
    build_os = 'OS_X'
else:
    # Unsupported platform.
    assert False

# Copied from https://docs.python.org/3.5/library/platform.html#cross-platform.
is_64bits = sys.maxsize > 2**32
#
# Support code
# ============
# xqt
# ---
# Pronounced "execute": provides a simple way to execute a system command.
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
    # instead of passing ``stdout=subprocess.DEVNULL`` to ``check_call``).
    for _ in cmds:
        # Per http://stackoverflow.com/questions/15931526/why-subprocess-stdout-to-a-file-is-written-out-of-order,
        # the ``check_call`` below will flush stdout and stderr, causing all
        # the subprocess output to appear first, followed by all the Python
        # output (such as the print statement above). So, flush the buffers to
        # avoid this.
        flush_print(_)
        # Use bash instead of sh, so that ``source`` and other bash syntax
        # works. See https://docs.python.org/3/library/subprocess.html#subprocess.Popen.
        executable = ('/bin/bash' if build_os == 'Linux' or build_os == 'OS_X'
                      else None)
        check_call(_, shell=True, executable=executable, **kwargs)
#
# pushd
# -----
# A context manager for pushd.
class pushd:
    def __init__(self,
      # The path to change to upon entering the context manager.
      path):

        self.path = path

    def __enter__(self):
        flush_print('pushd {}'.format(self.path))
        self.cwd = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, type_, value, traceback):
        flush_print('popd - returning to {}.'.format(self.cwd))
        os.chdir(self.cwd)
        return False
#
# system_identify
# ---------------
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
    elif build_os == 'OS_X':
        release, (version, dev_stage, non_release_version), machine = \
          platform.mac_ver()
        plat_str = ('release {}, dev stage {}, non-relase version {}, machine '
          '{}'.format(release, version, dev_stage, non_release_version,
                      machine))
    system, release, version = platform.system_alias(platform.system(),
      platform.release(), platform.version())
    flush_print('Python {}, OS {}, platform {} {} - {}'.format(sys.version, os.name,
      system, release, version, plat_str))
#
# command_line_invoke
# -------------------
# Command line processing: invoke ``install`` or ``test`` based on command-line
# arguments.
def command_line_invoke(
  # A funtion to invoke when ``argv[1] == 'install'``.
  install,
  # A function to invoke when ``argv[1] == 'test'``.
  test):

    assert len(sys.argv) == 2
    if sys.argv[1] == 'install':
        install()
    elif sys.argv[1] == 'test':
        test()
    else:
        raise RuntimeError('Unknown argument ' + sys.argv[1])
#
# OS_Dispatcher
# =============
# This class dispatches its methods to their OS-specific variants. For example,
# when ``build_os = 'Linux'``, ``o = OS_Dispatcher(); o.foo()`` invokes
# ``foo_Linux``.
class OS_Dispatcher:
    def __getattr__(self, name):
        return self.__getattribute__(name + '_' + build_os)
#
# Common tools
# ============
# wget
# ----
def wget(src, dst=None):
    flush_print('wget {} {}'.format(src, dst if dst else ''))
    wget_.download(src, dst)
#
# chdir
# -----
def chdir(path):
    flush_print('cd ' + path)
    os.chdir(path)
#
# mkdir
# -----
def mkdir(path):
    flush_print('mkdir ' + path)
    os.mkdir(path)
#
# unzip
# -----
# This is a thin wrapper around `ZipFile <https://docs.python.org/3/library/zipfile.html>`_.
def unzip(
  # The ``.zip`` file (including its extension) to unzip.
  zip_file,
  # The file to extract, a file of files to extract, or None to extrat all.
  # Note that paths must use a ``/``, even on Windows.
  file_to_extract=None,
  # A different directory to extract to; otherwise, this uses the current
  # working directory.
  path=None,
  # The password used for encrypted files.
  pwd=None):

    flush_print('unzip {} {} {} {}'.format(zip_file, file_to_extract or '',
      path or '', '*****' if pwd else ''))
    with ZipFile(zip_file) as zf:
        if isinstance(file_to_extract, str):
            zf.extract(file_to_extract, path, pwd)
        else:
            zf.extractall(path, file_to_extract, pwd)
#
# flush_print
# -----------
# Anything sent to ``print`` won't be printed until Python flushes its buffers,
# which means what CI logs report may be reflect what's actually being executed
# -- until the buffers are flushed.
def flush_print(*args, **kwargs):
    print(*args, **kwargs)
    # Flush both buffers, just in case there's something in ``stdout``.
    sys.stdout.flush()
    sys.stderr.flush()
#
# isfile
# ------
def isfile(f):
    _ = os.path.isfile(f)
    flush_print('File {} {}.'.format(f, 'exists' if _ else 'does not exist'))
    return _
#
# isfile
# ------
def isdir(f):
    _ = os.path.isdir(f)
    flush_print('Directory {} {}.'.format(f, 'exists' if _ else 'does not exist'))
    return _

