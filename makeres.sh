#/bin/sh

#env LD_PRELOAD="/usr/local/lib/libprofiler.so" python -m yep ./editor.py verybigfile.cpp
ulimit -c unlimited
python ./editor.py verybigfile.cpp