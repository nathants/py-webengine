#!/usr/bin/env python3
# type: ignore
import sys
import os
import pytest
import time
import requests
import webengine
import subprocess

class Main(webengine.Thread):
    def main(self):
        self.load('http://localhost:8081')

        # check the network requests
        assert ['get', 'http://localhost:8081/'] == self.network_requests[0]

        # check the link names
        self.wait_for_attr('a', 'innerText', ['HOME', 'PAGE-1', 'BROKEN-LINK'])

        # check the link hrefs
        p = 'http://localhost:8081/#' # prefix
        self.wait_for_attr('a', 'href', [f'{p}/', f'{p}/page1', f'{p}/nothing-to-see/here'])

        # should start on the homepage
        assert '/' == self.location()
        self.wait_for_attr('#content', 'innerText', ['home page'])

        # click on "page 1" and check contents
        self.click('a#page-1')
        self.wait_for_attr("#content p", 'innerText', ['this is a page with some data: 0'])
        self.wait_for_attr("#content button", 'innerText', ['PUSH ME'])

        # try clicking the button a few times
        for i in range(10):
            self.click("#content button")
            self.wait_for_attr("#content p:first-of-type", 'innerText', [f'this is a page with some data: {i + 1}'])

        # click on "broken link" and check contents
        self.click('a#broken-link')
        self.wait_for_attr("#content p", 'innerText', ['404'])

        # go back to home page should work
        self.click('a#home')
        self.wait_for_attr("#content", 'innerText', ['home page'])

        # go back to "page 1" and check contents is still 10
        self.click('a#page-1')
        self.wait_for_attr("#content p", 'innerText', ['this is a page with some data: 10'])

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
    # compile and run client webapp
    server = subprocess.Popen('port=8081 runclj client.cljs', shell=True)
    try:
        # wait for http server to come up
        for _ in range(500):
            try:
                requests.get('http://localhost:8081').status_code == 200
            except:
                time.sleep(.1)
            else:
                break
        else:
            assert False
        # run webengine
        webengine.run_thread(Main)
    finally:
        # stop server
        server.terminate()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(pytest.main(['test.py', '-svvx', '--tb', 'native']))
