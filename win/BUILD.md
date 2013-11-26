Building qutepart
==========

Downloads
-------------
- Download and install [CMake binary](http://www.cmake.org/). Tested with 2.8.12.
- Download and install Microsoft Visual Studio 2008 Express Edition (or the full version).
- Create a root directory and place the following as subdirectories in it:
    - Download [pcre source](http://www.pcre.org/). Tested with v. 8.33.
    - Download [ctags binary](http://ctags.sourceforge.net/). Tested with v. 5.8.
    - `git clone https://github.com/hlamer/qutepart` or download qutepart sources.

Make pcre
------------
    cd <root dir to pcre-8.33 source>
    cmake pcre-8.33 -D BUILD_SHARED_LIBS:BOOL=OFF -D PCRE_SUPPORT_UTF:BOOL=ON --build pcre-8.33-bin -G "Visual Studio 9 2008"
Then open the resulting `pcre-8.33-bin/PCRE.sln` in Visual Studio 2008, choose the release build configuration, then build `pcre`.

Build/install Python modules
----------------------------------
    cd qutepart
    python setup.py install --include-dir=..\pcre-8.33-bin --include-dir=win --lib-dir=..\pcre-8.33-bin\Release
