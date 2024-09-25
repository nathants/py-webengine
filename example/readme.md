in this example we will test the frontend from [aws-gocljs](https://github.com/nathants/aws-gocljs).

a live demo is [here](https://gocljs.nathants.com).

we have included:

- `frontend/public/index.html.gz`

which is output from:

- [aws-gocljs/bin/ensure.sh](https://github.com/nathants/aws-gocljs/blob/master/bin/ensure.sh)

if you have the dependencies installed, run:

```bash
python test.py
```

otherwise use x11 docker:

```bash
docker run \
    -h $HOSTNAME \
    -e XAUTHORITY=/code/.Xauthority \
    -v $HOME/.Xauthority:/code/.Xauthority \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY \
    --ipc host \
    -v $(pwd)/example:/example \
    py-webengine \
    sh -c 'python3 /example/test.py'
```

or headless docker:

```bash
docker run \
    -it \
    -v $(pwd)/example:/example \
    py-webengine \
    sh -c 'xvfb-run python3 /example/test.py'
```

example:

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
