# py-webengine

## what

browser automation from python with pyqt6-webengine.

you can:
- execute js
- inspect the attributes of elements
- use native mouse input
- use native keyboard input

## install and run

mac

```bash
brew install python3
brew install qt6
python3 -m pip install git+https://github.com/nathants/py-webengine
``

linux

```bash
apt-get install -y qt6-webengine-dev
pacman -S qt6-webengine
python3 -m pip install git+https://github.com/nathants/py-webengine
``


## example

[testing a react app](https://github.com/nathants/py-webengine/blob/master/example/)

```bash
python3 example/test.py
```

![](https://github.com/nathants/py-webengine/raw/master/demo.gif)
