#!/bin/bash
#
set -v
# Note: the ``-v`` flag echos commands in addition to executing them, per http://www.faqs.org/docs/abs/HTML/options.html.
#
# **********************************************
# osx_python_install.sh - Install Python on OS X
# **********************************************
# Perform the manual steps on OS X to install python3 and
# activate venv, since Python support is not available, per the list of `unsupported languages on OS X <https://github.com/travis-ci/travis-ci/issues/2320>`_.
# The following approach is based on a `workaround <https://github.com/travis-ci/travis-ci/issues/2312#issuecomment-195620855>`_.
# This was modified based on `instructions to install multiple Python versions on OS X <https://gist.github.com/Bouke/11261620>`_.
# See also the `pyenv docs <https://github.com/yyuu/pyenv/blob/master/README.md>`_.
#
# This is fairly noisy, so discard the output.
brew update > /dev/null
# Per the `pyenv homebrew recommendations <https://github.com/yyuu/pyenv/wiki#suggested-build-environment>`_.
brew install openssl readline
# Since pyenv is already installed, we need to do an upgrade instead.
# See https://docs.travis-ci.com/user/osx-ci-environment/#A-note-on-upgrading-packages.
brew outdated pyenv || brew upgrade pyenv
# virtualenv doesn't work without pyenv knowledge. venv in Python 3.3
# doesn't provide Pip by default. So, use `pyenv-virtualenv <https://github.com/yyuu/pyenv-virtualenv/blob/master/README.md>`_.
brew install pyenv-virtualenv
pyenv install $PYTHON
# I would expect something like ``pyenv init; pyenv local $PYTHON`` or
# ``pyenv shell $PYTHON`` would work, but ``pyenv init`` doesn't seem to
# modify the Bash environment. ??? So, I hand-set the variables instead.
export PYENV_VERSION=$PYTHON
export PATH="/Users/travis/.pyenv/shims:${PATH}"
pyenv-virtualenv venv
# Avoid printing the lines from the script below.
set +v
source venv/bin/activate
# A manual check that the correct version of Python is running.
python --version

