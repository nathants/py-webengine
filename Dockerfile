FROM archlinux:latest

RUN echo "Server = https://mirrors.xtom.com/archlinux/\$repo/os/\$arch" >  /etc/pacman.d/mirrorlist
RUN echo "Server = https://mirror.lty.me/archlinux/\$repo/os/\$arch"    >> /etc/pacman.d/mirrorlist

# install py-webengine dependencies
RUN pacman -Syu --noconfirm \
    git \
    python-pip \
    python-pyqt6 \
    python-pyqt6-webengine \
    xorg-server-xvfb

# install py-webengine
RUN python -m pip install \
    git+https://github.com/nathants/py-webengine \
    pytest

COPY . /code

WORKDIR /code

ENV QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu"

ENTRYPOINT ["xvfb-run", "-d", "python3", "example/test.py"]
