#!/usr/bin/env python3
import os
import pytest
import time
import requests
import webkit
import subprocess

class Main(webkit.Thread):
    def attr(self, selector, attr):
        return self.js(f'[...document.querySelectorAll("{selector}")].map(x => x.{attr})')

    def location(self):
        return self.js('document.location.href.split("/#")[1]')

    def click(self, selector):
        return self.js(f'document.querySelectorAll("{selector}")[0].click()')

    def main(self):
        self.load('http://localhost:8080')

        # check the link names
        assert ['home', 'page 1', 'broken link'] == self.attr('a', 'innerText')

        # check the link hrefs
        assert ['/', '/page1', '/nothing-to-see/here'] == [x.split('/#')[-1] for x in self.attr('a', 'href')]

        # should start on the homepage
        assert '/' == self.location()
        assert ['home page'] == self.attr('#content *', 'innerHTML')

        # click on "page 1" and check contents
        self.click('a#page1')
        self.wait_for_dom_changes()
        assert '/page1' == self.location()
        assert ['this is a page with some data: 0'] == self.attr("#content p:first-of-type", 'innerText')
        assert ['push me'] == self.attr("#content input:first-of-type", 'value')

        # try clicking the button a few times
        for i in range(10):
            self.click("#content input")
            self.wait_for_dom_changes()
            assert [f'this is a page with some data: {i + 1}'] == self.attr("#content p:first-of-type", 'innerText')

        # click on "broken link" and check contents
        self.click('a#broken')
        self.wait_for_dom_changes()
        assert '/nothing-to-see/here' == self.location()
        assert ['404'] == self.attr("#content p", 'innerText')

        # go back to home page should work
        self.js('document.querySelectorAll("a")[0].click()')
        self.wait_for_dom_changes()
        assert '/' == self.location()
        assert ['home page'] == self.attr("#content *", 'innerHTML')

        # go back to "page 1" and check contents is still 10
        self.click('a#page1')
        self.wait_for_dom_changes()
        assert ['this is a page with some data: 10'] == self.attr("#content p:first-of-type", 'innerText')

        # save a screenshot
        image = '/tmp/screen.png'
        self.screenshot(image)
        assert os.path.isfile(image)

def test():
    # compile and run client webapp
    server = subprocess.Popen('port=8080 runclj client.cljs', shell=True)
    try:
        # wait for http server to come up
        for _ in range(500):
            try:
                requests.get('http://localhost:8080').status_code == 200
            except:
                time.sleep(.1)
            else:
                break
        else:
            assert False
        # run webkit
        webkit.run_thread(Main)
    finally:
        # stop server
        server.terminate()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    pytest.main(['test.py', '-svvx', '--tb', 'native'])
