#!/bin/bash
#
set -v
# Note: the ``-v`` flag echos commands in addition to executing them, per http://www.faqs.org/docs/abs/HTML/options.html.
#
# **********************************************
# osx_python_install.sh - Install Python on OS X
# **********************************************
git clone https://github.com/MacPython/terryfy.git
# Avoid printing the lines from the script below.
set +v
source terryfy/travis_tools.sh
get_python_environment $INSTALL_TYPE $VERSION $VENV

