# type: ignore
# flake8: noqa
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtWidgets import QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
import traceback
import sys
import os
import time
import concurrent.futures
import collections

class NetworkInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, network_requests):
        super().__init__()
        self.network_requests = network_requests

    def interceptRequest(self, info):
        self.network_requests.append([bytes(info.requestMethod()).decode().lower(), bytes(info.requestUrl().toEncoded()).decode()])

class Thread(QThread):
    screenshot_signal = pyqtSignal(str)

    def __init__(self, app, browser, *a, **kw):
        super().__init__(*a, **kw)
        self.network_requests = collections.deque([], 1000)
        self.load_counter = 0
        self.app = app
        self.browser = browser
        self.last_dom = None
        self.network_interceptor = NetworkInterceptor(self.network_requests)
        self.browser.page().profile().setUrlRequestInterceptor(self.network_interceptor)

    def screenshot(self, path):
        assert path.endswith('.jpg') or path.endswith('.png')
        self.screenshot_signal.emit(path)

    def js(self, code):
        f = concurrent.futures.Future()
        self.browser.page().runJavaScript(code, f.set_result)
        return f.result()

    def wait_for_dom_changes(self):
        for _ in range(1000):
            time.sleep(.01)
            if self.last_dom != self.js('document.body.innerHTML'):
                self.last_dom = self.js('document.body.innerHTML')
                return
        assert False, 'timeout'

    def load(self, url):
        if '://' not in url:
            url = f'https://{url}'
        # load a blank page before clearing network requests
        count = self.load_counter
        self.js(f'document.location.href = "http://127.0.0.1:1"')
        while True:
            if self.load_counter == count + 1:
                break
            time.sleep(.01)
        # clear network requests
        self.network_requests.clear()
        # now that network requests are clear and the page is empty, load the next page
        count = self.load_counter
        self.js(f'document.location.href = "{url}"')
        while True:
            if self.load_counter == count + 1:
                break
            time.sleep(.01)
        self.last_dom = self.js('document.body.innerHTML')

    def run(self):
        while True:
            if self.load_counter == 1:
                break
            time.sleep(.01)
        try:
            self.main()
        except:
            traceback.print_exc()
            self.app.exit(1)
        else:
            self.app.exit(0)

    def main(self):
        assert False, 'please implement main()'

class Window(QMainWindow):
    def __init__(self, app, thread, devtools, page_zoom, devtools_zoom, dimensions):
        assert not devtools or devtools in {'horizontal', 'vertical'}
        super().__init__()
        if dimensions and dimensions[0] and dimensions[1]:
            self.setFixedSize(*dimensions)
        self.browser = QWebEngineView()
        self.t = thread(app, self.browser)
        self.t.screenshot_signal.connect(self.screenshot)
        self.browser.setUrl(QUrl("http://127.0.0.1:1"))
        self.browser.page().loadFinished.connect(self.onload)
        self.browser.page().setZoomFactor(page_zoom)
        self.devtools = QWebEngineView()
        self.devtools.page().setZoomFactor(devtools_zoom)
        self.browser.page().setDevToolsPage(self.devtools.page())
        wid = QWidget(self)
        self.setCentralWidget(wid)
        if devtools == 'horizontal':
            box = QVBoxLayout()
        else:
            box = QHBoxLayout()
        box.addWidget(self.browser)
        if devtools:
            box.addWidget(self.devtools)
        wid.setLayout(box)
        self.show()
        self.t.start()

    @pyqtSlot(str)
    def screenshot(self, path):
        self.browser.grab().save(path)

    def onload(self, *a, **kw):
        self.t.load_counter += 1

def run_thread(thread_class, devtools=None, page_zoom=1.0, devtools_zoom=1.5, dimensions=(0, 0), qt_argv=['-platform', 'minimal']):
    app = QApplication(qt_argv)
    window = Window(app, thread_class, devtools, page_zoom, devtools_zoom, dimensions)
    if app.exec_() != 0:
        sys.exit(1)
