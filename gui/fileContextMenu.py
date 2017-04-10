# -*- coding: utf-8 -*-

import os

from PyQt5.QtWidgets import (
    QAction,
    QMenu,
)
from . import runDlg
import subprocess


class FileContextMenu(QMenu):
    def __init__(self, info, parent=None):
        super(FileContextMenu, self).__init__(parent)
        self.p = parent
        
        self.path = str(info.filePath())
        
        path, file_name = os.path.split(self.path)
        
        self.info = info
        
        folder_list = []
        
        while True:
            path, folder = os.path.split(path)
            if folder != '':
                folder_list.append(folder)
            else:
                break
            
        if 'exe' in file_name:
            exePath = os.path.join(self.path, 'exePath')
            if os.path.exists(exePath):
                self.add('Run', self.run)
                
    def add(self, name, func):
        action = QAction(name, self)
        action.triggered.conncet(func)
        self.addAction(action)
        
    def run(self):
        form = runDlg.StringListDlg(self)
        form.exec_()
