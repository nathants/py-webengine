#!/usr/bin/env python3
# type: ignore
import sys
import os
import pytest
import time
import webengine
import subprocess

host = 'http://localhost:8000'

class Main(webengine.Runner):
    action_delay_seconds = 0.1

    def location(self):
        return self.js('document.location.href.split("/#")[1]')

    def main(self):
        # wait for the HTTP server to come up and the site to load properly
        for _ in range(100):
            try:
                self.load(host)
                self.wait_attr('a', 'innerText', ['home', 'files', 'api', 'websocket'])
            except:
                print('Waiting for site to be ready...')
                time.sleep(0.1)
            else:
                break
        else:
            assert False, "Site did not become ready in time."

        # load the site
        self.load(host)

        # check the network requests
        assert ['get', host + '/'] == self.network_requests[0], "Unexpected network request."

        # check the link names
        self.wait_attr('a', 'innerText', ['home', 'files', 'api', 'websocket'])

        # check the link hrefs
        expected_hrefs = [
            f'{host}/#/home',
            f'{host}/#/files',
            f'{host}/#/api',
            f'{host}/#/websocket'
        ]
        self.wait_attr('a', 'href', expected_hrefs)

        # ensure the homepage is loaded
        assert '/' == self.location(), "Homepage not loaded correctly."
        self.wait_attr('#content', 'innerText', ['home'])

        # click on 'files' and verify contents
        self.click('a#files')
        self.wait_attr("#content p", 'innerText', ["files"])

        # click on 'websocket' and verify contents
        self.click('a#websocket')
        self.wait_attr("#content p", 'innerText', lambda texts: texts[0].startswith('time:'))

        # interact with the search input
        self.click('input#search')
        self.type("a/b/c")
        self.enter()
        self.wait_attr("#content p", 'innerText', ['a', 'b', 'c', 'Enter'])

        # navigate back to the home page
        self.click('a#home')
        self.wait_attr("#content", 'innerText', ['home'])

        # take a screenshot of the current state
        image = '/tmp/screen.png'
        if os.path.isfile(image):
            os.remove(image)
        self.screenshot(image)
        for _ in range(100):
            if os.path.isfile(image):
                break
            time.sleep(0.1)
        else:
            assert False, 'no screenshot found'

def test():
    subprocess.check_call('gunzip --force --keep index.html.gz', shell=True)
    server = subprocess.Popen('python3 -m http.server', shell=True)
    try:
        time.sleep(1)
        code = webengine.run(Main)
        if code != 0:
            sys.exit(code)
    finally:
        server.terminate()
        server.wait()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(pytest.main([__file__, '-svvx', '--tb', 'native']))
