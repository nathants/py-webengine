#!/bin/bash
set -eou pipefail
sudo pacman -Sy --noconfirm \
     git \
     python-pip \
     python-pyqt5 \
     python-pyqtwebengine \
     xorg-server-xvfb
sudo python -m pip install git+https://github.com/nathants/py-webengine
