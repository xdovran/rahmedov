import contextlib
import os

from PyQt5.QtCore import QRect, QSettings
from PyQt5.QtGui import (
    QIcon,
)
from PyQt5.QtWidgets import QApplication, QSplitter, QStyleFactory, QVBoxLayout, QWidget

from . import explorer, toolBar, window


class Gui(QWidget):
    def __init__(self, root, parent=None):
        super(Gui, self).__init__(parent)

        self.root = root
        self.p = self

        self.settings = QSettings()

        self.iconList = (
            ':/scorpion_black.png',
            ':/scorpion_blue.png',
            ':/scorpion_green.png',
            ':/scorpion_orange.png',
            ':/scorpion_red.png',
            ':/scorpion_violet.png',
        )

        self.appPath = os.path.dirname(
            os.path.realpath(__file__))

        self.guiPath, self.guiName = os.path.split(self.appPath)
        self.cfgDirPath = self.guiPath

        self.setWindowTitle(root + ': ' + self.guiPath)

        self.cssFile = os.path.join(
            self.appPath, 'qdarkstyle', 'style.qss')

        with contextlib.closing(
                open(self.cssFile, 'r')) as self.cssFile:
            self.setStyleSheet(self.cssFile.read())
        QApplication.setStyle(
            QStyleFactory.create('Cleanlooks'))

        self.setWindowIcon(self.settings.value(
            'guiIcon', QIcon(self.iconList[0]), type=QIcon))

        self.setGeometry(self.settings.value(
            'guiGeometry',
            QRect(100, 100, 1030, 800),
            type=QRect))

        self.explorer = explorer.Explorer(self)
        self.window = window.Window(self)

        self.split = QSplitter()
        self.split.addWidget(self.explorer)
        self.split.addWidget(self.window)
        self.split.setSizes(self.settings.value(
            'splitSize',
            [120, 720],
            type=int))

        self.toolbar = toolBar.ToolBar(self)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.split)

        self.setLayout(self.layout)

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue('splitterSize', self.split.sizes())
        settings.setValue('guiIcon', self.windowIcon())
        settings.setValue('guiGeometry', self.geometry())
