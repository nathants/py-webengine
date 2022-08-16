# py-webengine

## why

browser testing is annoying, brittle, and slow.

## what

easy and fun browser testing from python with pyqt6-webengine.

## how

execute javascript.

inspect network requests.

send native mouse and keyboard input.

wait for values to show up on screen.

make assertions.

## install and run

mac

```bash
brew install python3
brew install qt6
python3 -m pip install git+https://github.com/nathants/py-webengine
```

linux

```bash
apt-get install -y qt6-webengine-dev                                # debian/ubuntu
pacman -S qt6-webengine                                             # arch
python3 -m pip install git+https://github.com/nathants/py-webengine # all platforms
```

## api

```python

class webengine.Thread:

    action_delay_seconds = .01 # seconds between browser actions

    timeout_seconds = 10 # maximum seconds to wait_attr()

    def js(self, code):
        "execute javascript and return the result as a string"

    def click(self, selector):
        "send native mouse input at the center of the first element matching selector"

    def type(self, value):
        "send native keyboard input, one character at a time"

    def enter(self):
        "send native keyboard input enter"

    def attr(self, selector, attr):
        "return the list of the attribute for all elements matching selector"

    def wait_attr(self, selector, attr, value):
        "wait for the attribute of all elements matching a selector have the given value"

    def load(self, url):
        "load url"

    def screenshot(self, path):
        "save a png or jpg at path"

    def run(self):
        "run the main method"

    def main(self):
        "implement this method as your test"

```


## usage

subclass `webengine.Thread` and implement `main()`:

```python

host = 'http://localhost:8000'

class Main(webengine.Thread):

    action_delay_seconds = .025

    def main(self):

        # wait for http server to come up and the site to load properly
        for _ in range(100):
            try:
                self.load(host)
                self.wait_attr('a', 'innerText', ['home', 'files', 'api', 'websocket'])
            except:
                print('wait for site to be ready')
                time.sleep(.1)
            else:
                break
        else:
            assert False

        # load the site
        self.load(host)

        # click on files and check contents
        self.click('a#files')
        self.wait_attr("#content p", 'innerText', ["files"])
```

then invoke your test:

```python
def test():
    # build your webapp
    subprocess.check_call('gunzip --force --keep index.html.gz', shell=True)
    # run your webapp
    server = subprocess.Popen('python3 -m http.server', shell=True)
    try:
        # run webengine
        webengine.run_thread(Main, devtools='horizontal')
    finally:
        # stop webapp
        server.terminate()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(pytest.main(['test.py', '-svvx', '--tb', 'native']))
```

to leave the browser open, insert somewhere in your test:

```python
time.sleep(1000)
```

to drop into a python repl, first install [ipdb](https://github.com/gotcha/ipdb):

```bash
python3 -m pip install ipdb
```

then insert somewhere in your test:

```python
import ipdb; ipdb.set_trace()
```

run x11 docker:

```bash
docker run \
    -h $HOSTNAME \
    -e XAUTHORITY=/code/.Xauthority \
    -v $HOME/.Xauthority:/code/.Xauthority \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY \
    --ipc host \
    py-webengine \
    sh -c 'python3 example/test.py'
```

run headless docker:

```bash
docker run \
    -it \
    -v $(pwd)/example:/example \
    py-webengine \
    sh -c 'xvfb-run python3 /example/test.py'
```

docker example:

```bash
>> docker build -t py-webengine .

>> docker run -it --rm py-webengine

wait for: a innerText ['home', 'files', 'api', 'websocket']
wait for: a href ['http://localhost:8000/#/home', 'http://localhost:8000/#/files', 'http://localhost:8000/#/api', 'http://localhost:8000/#/websocket']
wait for: #content innerText ['home']
wait for: #content p innerText ['files']
wait for: #content p innerText 'predicate(x)'
wait for: #content p innerText ['a', 'b', 'c', 'Enter']
wait for: #content innerText ['home']
PASSED
```

see the [example](https://github.com/nathants/py-webengine/blob/master/example/) for detailed usage.

in the example we will test the frontend from [aws-gocljs](https://github.com/nathants/aws-gocljs).

a live demo of that site is [here](https://gocljs.nathants.com).

## demo

![](https://github.com/nathants/py-webengine/raw/master/demo.gif)
