# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication, QPushButton

class Kasse(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Hello, world!'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        button = QPushButton('Click me', self)
        button.move(100, 70)

        self.show()

application = QApplication(sys.argv)
root = Kasse()
sys.exit(application.exec_())