#!/usr/bin/env python3
# type: ignore
import sys
import os
import pytest
import time
import webengine
import subprocess

host = 'http://localhost:8000'

class Main(webengine.Thread):

    action_delay_seconds = .025

    def location(self):
        return self.js('document.location.href.split("/#")[1]')

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

        # check the network requests
        assert ['get', host + '/'] == self.network_requests[0]

        # check the link names
        self.wait_attr('a', 'innerText', ['home', 'files', 'api', 'websocket'])

        # check the link hrefs
        self.wait_attr('a', 'href', [f'{host}/#/home', f'{host}/#/files', f'{host}/#/api', f'{host}/#/websocket'])

        # should start on the homepage
        assert '/' == self.location()
        self.wait_attr('#content', 'innerText', ['home'])

        # click on files and check contents
        self.click('a#files')
        self.wait_attr("#content p", 'innerText', ["files"])

        # click on websocket and check contents
        self.click('a#websocket')
        self.wait_attr("#content p", 'innerText', lambda x: x[0].startswith('time:'))

        # click on search, type some stuff, hit enter, and check contents
        self.click('input#search')
        self.type("a/b/c")
        self.enter()
        self.wait_attr("#content p", 'innerText', ['a', 'b', 'c', 'Enter'])

        # go back to home page should work
        self.click('a#home')
        self.wait_attr("#content", 'innerText', ['home'])

        # save a screenshot
        image = '/tmp/screen.png'
        if os.path.isfile(image):
            os.remove(image)
        self.screenshot(image)
        for _ in range(100):
            if os.path.isfile(image):
                break
            time.sleep(.1)
        else:
            assert False, 'no screenshot found'

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
