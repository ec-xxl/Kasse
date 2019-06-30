# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication, QPushButton, QVBoxLayout


# ---------------------------------------------- #
# ------------- Create root window ------------- #
# ---------------------------------------------- #

application = QApplication(sys.argv)

root = QWidget()
root.show()

sys.exit(application.exec_())