FROM archlinux:latest

RUN echo 'Server = https://mirrors.kernel.org/archlinux/$repo/os/$arch' > /etc/pacman.d/mirrorlist

RUN pacman -Syu --noconfirm \
    entr \
    git \
    python-pip \
    python-pyqt5 \
    python-pyqtwebengine \
    xorg-server-xvfb

RUN python -m pip install \
    git+https://github.com/nathants/py-webengine \
    pytest

COPY . /code

WORKDIR /code

ENV QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu"

ENTRYPOINT ["xvfb-run", "-d", "python3", "test.py"]
