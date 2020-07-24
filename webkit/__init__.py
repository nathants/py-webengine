# type: ignore
# flake8: noqa
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import traceback
import sys
import os
import time
import concurrent.futures

class Thread(QThread):
    screenshot_signal = pyqtSignal(str)

    def __init__(self, app, browser, *a, **kw):
        super().__init__(*a, **kw)
        self.load_counter = 0
        self.app = app
        self.browser = browser
        self.last_dom = None

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
        count = self.load_counter
        self.js(f'document.location.href = "{url}"')
        while True:
            if self.load_counter == count + 1:
                break
            time.sleep(.01)
        self.last_dom = self.js('document.body.innerHTML')

    def _browser_ready(self):
        while True:
            if self.load_counter == 1:
                break
            time.sleep(.01)

    def run(self):
        self._browser_ready()
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
        self.setFixedSize(*dimensions)
        self.browser = QWebEngineView()
        self.t = thread(app, self.browser)
        self.t.screenshot_signal.connect(self.screenshot)
        self.browser.setUrl(QUrl("http://127.0.0.1"))
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

def run_thread(thread_class, devtools=None, page_zoom=1.0, devtools_zoom=1.5, dimensions=(1024, 1024), qt_argv=[]):
    app = QApplication(qt_argv)
    window = Window(app, thread_class, devtools, page_zoom, devtools_zoom, dimensions)
    if app.exec_() != 0:
        sys.exit(1)
