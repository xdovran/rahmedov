# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QLabel

from PyQt5.QtCore import Qt

class GenericImage(QLabel):
    def __init__(self, parent = None):
        QLabel.__init__(self, parent)
        self.setMinimumSize(200, 200)
        self.setAlignment(Qt.AlignCenter)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
