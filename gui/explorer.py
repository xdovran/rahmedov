from PyQt5.QtWidgets import (
    QWidget,
    QStackedWidget,
    QFileSystemModel,
    QTreeView,
    QAction,
    QToolBar,
    QLineEdit,
    QVBoxLayout,
)
from PyQt5.QtGui import (
    QIcon,
)

from PyQt5.QtCore import (
    Qt,
    QModelIndex
)
from . import fileContextMenu
#import resource_files

class Explorer(QStackedWidget):
    def __init__(self, parent):
        QStackedWidget.__init__(self, parent)
        self.p = parent
        self.layerSet = {}

    def setLayer(self, s):        
        self.setCurrentWidget(self.layerSet[s])

    def addLayer(self, rootPath):        
        if rootPath in self.layerSet:            
            self.setLayer(rootPath)
        else:            
            fileSystemExplorer = FileSystemExplorer(rootPath, self.p)
            self.layerSet[rootPath] = fileSystemExplorer
            self.addWidget(fileSystemExplorer)

    def removeLayer(self, s):
        w =  self.layerSet[s]
        del self.layerSet[s]
        w.deleteLater()
        self.removeWidget(w)


class SystemModel(QFileSystemModel):
    def __init__(self, parent= None):        
        QFileSystemModel.__init__(self, parent)

    def columnCount(self, parent = QModelIndex()):
        return 1

class Tree(QTreeView):
    def __init__(self, parent = None, main = None, r=''):        
        QTreeView.__init__(self, parent)
        self.p = main
        self.window = main.window
        
        self. dirPath = r
        
        self.reset2()
        
        self.activated.connect(self.treeActivated)                
        
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

    def openMenu(self, position):
        info = self.model.fileInfo(self.currentIndex())
        m = fileContextMenu.FileContextMenu(info, self.p)
        m.exec_(self.viewport().mapToGlobal(position)) # position menu and show it
              
    def treeActivated(self, i):
        self.window.currentWidget().treeActivated(self.model.fileInfo(i))
    
    def currentChanged(self, i, j):        
        self.window.currentWidget().treeCurrentChanged(self.model.fileInfo(i))
    
    def reset2(self):        
        self.model = SystemModel(self)
        root = self.model.setRootPath(self. dirPath)
        self.setModel(self.model)
        self.setRootIndex(root)

# This is added as a tab to Explorer:
class FileSystemExplorer(QWidget):
    def __init__(self, rootPath, parent):
        QWidget .__init__(self, parent)

        self.p = parent    

        layout = QVBoxLayout(self)

        tool = QToolBar()
                
        lineEdit = QLineEdit(parent=tool)

        tree = Tree(parent=self, main=self.p, r=rootPath)

        refresh = QAction(QIcon(":/refresh.png"), "&New", tool)
        refresh.triggered.connect(tree.reset2)

        tool.addWidget(lineEdit)
        tool.addAction(refresh)
             
        layout.addWidget(tool)        
        
        layout.addWidget(tree)
        self.setLayout(layout)
