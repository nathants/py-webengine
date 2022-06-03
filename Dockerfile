FROM debian:testing

RUN apt-get update

# install py-webengine dependencies
RUN apt-get install -y \
    git \
    libasound2 \
    python3-pip \
    qt6-webengine-dev/testing \
    xvfb

# install py-webengine
RUN python3 -m pip install \
    git+https://github.com/nathants/py-webengine \
    pytest

COPY . /code

WORKDIR /code

ENV QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu"

CMD xvfb-run python3 example/test.py
