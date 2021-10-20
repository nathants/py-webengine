#!/bin/bash
set -eou pipefail
sudo pacman -Sy --noconfirm \
     git \
     python-pip \
     python-pyqt6 \
     python-pyqt6-webengine \
     xorg-server-xvfb
sudo python -m pip install git+https://github.com/nathants/py-webengine
