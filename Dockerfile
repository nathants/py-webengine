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
    pytest

RUN groupadd -g 1000 py-webengine

RUN useradd -d /code -s /bin/bash -m py-webengine -u 1000 -g 1000

USER py-webengine

ENV HOME /code

COPY --chown=py-webengine:py-webengine . /code

RUN python3 -m pip install /code

WORKDIR /code

ENV QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu"

CMD xvfb-run python3 example/test.py
