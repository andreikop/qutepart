#!/bin/bash
#
set -v
# Note: the ``-v`` flag echos commands in addition to executing them, per http://www.faqs.org/docs/abs/HTML/options.html.

sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
sudo apt-get update
sudo apt-get install -y libpcre3-dev libegl1-mesa libstdc++6

export DISPLAY=:99.0
