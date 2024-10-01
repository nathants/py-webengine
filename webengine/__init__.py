#!/usr/bin/env python3
import sys
import os
import time
import traceback
import subprocess
import collections
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt6.QtCore import QUrl, QThread, pyqtSignal, pyqtSlot, QEvent, QPointF, Qt, QObject
from PyQt6.QtGui import QMouseEvent, QKeyEvent

host = 'http://localhost:8000'

class NetworkInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, network_requests):
        super().__init__()
        self.network_requests = network_requests

    def interceptRequest(self, info):
        method = info.requestMethod().data().decode('utf-8').lower()
        url = info.requestUrl().toString()
        if not url.startswith('devtools://'):
            self.network_requests.append([method, url])

class Runner(QObject):
    load_url_signal = pyqtSignal(str)
    run_js_signal = pyqtSignal(str)
    click_signal = pyqtSignal(str)
    type_signal = pyqtSignal(str)
    enter_signal = pyqtSignal()
    screenshot_signal = pyqtSignal(str)
    exit_signal = pyqtSignal(int)
    wait_attr_signal = pyqtSignal(str, str, object)
    js_result_signal = pyqtSignal(object)
    attr_result_signal = pyqtSignal(object)
    action_delay_seconds = 0.025
    timeout_seconds = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self.network_requests = collections.deque([], 1000)
        self.load_counter = 0
        self.js_result = None
        self.attr_result = None

    def js(self, code):
        self.js_result = None
        self.run_js_signal.emit(code)
        start_time = time.monotonic()
        while self.js_result is None:
            if time.monotonic() - start_time > self.timeout_seconds:
                raise TimeoutError
            time.sleep(0.01)
        return self.js_result

    def js_result_callback(self, result):
        self.js_result = result

    def attr_result_callback(self, result):
        self.attr_result = result

    def click(self, selector):
        self.click_signal.emit(selector)
        time.sleep(self.action_delay_seconds)

    def type(self, value):
        self.type_signal.emit(value)
        time.sleep(self.action_delay_seconds)

    def enter(self):
        self.enter_signal.emit()
        time.sleep(self.action_delay_seconds)

    def attr(self, selector, attr):
        self.attr_result = None
        self.wait_attr_signal.emit(selector, attr, None)
        start_time = time.monotonic()
        while self.attr_result is None:
            if time.monotonic() - start_time > self.timeout_seconds:
                raise TimeoutError
            time.sleep(0.01)
        return self.attr_result

    def wait_attr(self, selector, attr, value):
        start_time = time.monotonic()
        while True:
            attr_values = self.attr(selector, attr)
            print("wait", selector, attr, attr_values)
            if callable(value):
                if value(attr_values):
                    break
            elif attr_values == value:
                break
            if time.monotonic() - start_time > self.timeout_seconds:
                raise TimeoutError
            time.sleep(0.1)

    def load(self, url):
        count = self.load_counter
        start_time = time.monotonic()
        self.load_url_signal.emit(url)
        while self.load_counter == count:
            if time.monotonic() - start_time > self.timeout_seconds:
                raise TimeoutError
            time.sleep(0.01)

    def screenshot(self, path):
        self.screenshot_signal.emit(path)

    def run(self):
        try:
            self.main()
        except:
            traceback.print_exc()
            self.exit_signal.emit(1)
        else:
            self.exit_signal.emit(0)

    def main(self):
        raise NotImplementedError

class Window(QMainWindow):
    def __init__(self, app, runner, devtools='vertical', page_zoom=1.0, devtools_zoom=1.0, dimensions=None):
        super().__init__()
        self.app = app
        self.runner = runner()
        self.network_interceptor = NetworkInterceptor(self.runner.network_requests)
        if dimensions:
            self.setFixedSize(*dimensions)
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("about:blank"))
        self.browser.page().loadFinished.connect(self.onload)
        self.browser.page().setZoomFactor(page_zoom)
        self.browser.page().profile().setUrlRequestInterceptor(self.network_interceptor)
        orientation = Qt.Orientation.Horizontal if devtools == 'vertical' else Qt.Orientation.Vertical
        if devtools:
            wid = QWidget(self)
            self.setCentralWidget(wid)
            layout = QSplitter(orientation)
            layout.addWidget(self.browser)
            self.devtools = QWebEngineView()
            self.devtools.page().setZoomFactor(devtools_zoom)
            self.browser.page().setDevToolsPage(self.devtools.page())
            layout.addWidget(self.devtools)
            layout.setStretchFactor(0, 3)
            layout.setStretchFactor(1, 1)
            main_layout = QVBoxLayout()
            main_layout.addWidget(layout)
            wid.setLayout(main_layout)
            self.show()
        else:
            self.browser.show()
        self.runner.load_url_signal.connect(self.load_url)
        self.runner.run_js_signal.connect(self.run_js)
        self.runner.click_signal.connect(self.click_element)
        self.runner.type_signal.connect(self.type_text)
        self.runner.enter_signal.connect(self.press_enter)
        self.runner.screenshot_signal.connect(self.take_screenshot)
        self.runner.wait_attr_signal.connect(self.check_attribute)
        self.runner.exit_signal.connect(self.exit_app)
        self.runner.js_result_signal.connect(self.runner.js_result_callback)
        self.runner.attr_result_signal.connect(self.runner.attr_result_callback)
        self.thread = QThread()
        self.runner.moveToThread(self.thread)
        self.thread.started.connect(self.runner.run)
        self.thread.start()

    @pyqtSlot()
    def onload(self):
        self.runner.load_counter += 1

    @pyqtSlot(str)
    def load_url(self, url):
        self.browser.setUrl(QUrl(url))

    @pyqtSlot(str)
    def run_js(self, code):
        def js_callback(result):
            self.runner.js_result_signal.emit(result)
        self.browser.page().runJavaScript(code, js_callback)

    @pyqtSlot(str)
    def click_element(self, selector):
        def process_click(result):
            if not result:
                print(f"Element not found for selector: {selector}")
                return
            x, y, width, height = result
            center_x = x + width / 2
            center_y = y + height / 2
            position = QPointF(center_x, center_y)
            global_pos = self.browser.mapToGlobal(position.toPoint())
            global_position = QPointF(float(global_pos.x()), float(global_pos.y()))
            args = position, global_position, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier
            press_event = QMouseEvent(QEvent.Type.MouseButtonPress, *args)
            release_event = QMouseEvent(QEvent.Type.MouseButtonRelease, *args)
            QApplication.postEvent(self.browser.focusProxy(), press_event)
            QApplication.postEvent(self.browser.focusProxy(), release_event)
        code = f'''
            var element = document.querySelector("{selector}");
            if (element) {{
                var rect = element.getBoundingClientRect();
                [rect.x, rect.y, rect.width, rect.height];
            }} else {{
                null;
            }}
        '''
        self.browser.page().runJavaScript(code, process_click)

    @pyqtSlot(str)
    def type_text(self, value):
        for char in value:
            args = 0, Qt.KeyboardModifier.NoModifier, char
            press_event = QKeyEvent(QEvent.Type.KeyPress, *args)
            release_event = QKeyEvent(QEvent.Type.KeyRelease, *args)
            QApplication.postEvent(self.browser.focusProxy(), press_event)
            QApplication.postEvent(self.browser.focusProxy(), release_event)

    @pyqtSlot()
    def press_enter(self):
        args = Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier, "\r"
        press_event = QKeyEvent(QEvent.Type.KeyPress, *args)
        release_event = QKeyEvent(QEvent.Type.KeyRelease, *args)
        QApplication.postEvent(self.browser.focusProxy(), press_event)
        QApplication.postEvent(self.browser.focusProxy(), release_event)

    @pyqtSlot(str)
    def take_screenshot(self, path):
        self.browser.grab().save(path)

    @pyqtSlot(str, str, object)
    def check_attribute(self, selector, attr, value):
        code = f'''
            var elements = [...document.querySelectorAll("{selector}")];
            elements.map(x => x.{attr});
        '''

        def js_callback(result):
            self.runner.attr_result_signal.emit(result)
        self.browser.page().runJavaScript(code, js_callback)

    @pyqtSlot(int)
    def exit_app(self, code):
        self.thread.quit()
        self.thread.wait()
        self.app.exit(code)

def run(runner, devtools=None, page_zoom=1.0, devtools_zoom=1.0, dimensions=None):
    app = QApplication(sys.argv)
    window = Window(app, runner, devtools, page_zoom, devtools_zoom, dimensions)
    code = app.exec()
    return code
