#!/bin/bash
set -xeou pipefail

if ! which aws-ec2-new; then
    echo fatal: need to install https://github.com/nathants/cli-aws
    exit 1
fi

id=$(aws-ec2-new \
         --type c5d.large \
         --ami arch \
         py-webengine-test-box)

trap "aws-ec2-rm -y $id" EXIT

aws-ec2-ssh $id -yc '
    echo "Server = https://mirrors.kernel.org/archlinux/\$repo/os/\$arch" | sudo tee /etc/pacman.d/mirrorlist
    curl https://raw.githubusercontent.com/nathants/py-webengine/master/scripts/install_archlinux.sh | bash
    sudo pacman -Sy --noconfirm \
         leiningen \
         npm
    sudo npm install -g http-server
    if ! which runclj &>/dev/null; then (
        cd /tmp
        rm -rf runclj
        git clone https://github.com/nathants/runclj
        sudo mv runclj/bin/* runclj/bin/.lein/ /usr/local/bin
    ) fi
' >/dev/null

aws-ec2-ssh $id -yc '
    cd /tmp
    rm -rf py-webengine
    git clone https://github.com/nathants/py-webengine
    cd py-webengine
    sudo python -m pip install pytest requests
    export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu"
    xvfb-run -d -e error.log python example/test.py
' >/dev/null
