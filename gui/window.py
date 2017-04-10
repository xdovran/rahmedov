import os
from PyQt5.QtWidgets import (
    QStackedWidget,
    QTabWidget,
    QMainWindow,
    QMessageBox,
)
from PyQt5.QtCore import (
    Qt,
)

class Window(QStackedWidget):
    def __init__(self, parent):
        super(Window, self).__init__(parent)
        self.p = parent.p
        self.explorer = parent.explorer
        self.windowList = {}
        self.addWindows()
        self.layerSet = set()
        
    def setLayer(self, s):
        for w in self.windowList:
            self.windowList[w].setLayer(s)
            
    def addLayer(self, s):
        if s in self.layerSet:
            self.setLayer(s)
        else:
            self.layerSet.add(s)
            for w in self.windowList:
                self.windowList[w].addLayer(s)
                
    def removeLayer(self, s):
        self.layerSet.remove(s)
        for w in self.windowList:
            self.windowList[w].removeLayer(s)
            
    def addWindows(self):
        from txtWindow.txtWindow import TxtWindow
        name = 'Editor'
        self.editor = TxtWindow(self.p)
        self.addWidget(self.editor)
        self.windowList[name] = self.editor
        
        from imgWindow.imgWindow import ImgWindow
        name = 'Image'
        self.img = ImgWindow(self.p)
        self.addWidget(self.img)
        self.windowList[name] = self.img
        
    def setWindow(self, name):
        self.setCurrentWidget(self.windowList[name])
    
    def treeActivated(self, info):
        self.currentWidget().activate(info)
        
    def treeClicked(self, info):
        pass

    def treeEntered(self, info):
        pass
    
    def treeDoubleClicked(self, info):
        pass
    
    def treePressed(self, info):
        pass
    
    def treeCurrentChanged(self, info):
        pass


class Layer(QTabWidget):
    def __init__(self, s, view, parent=None):
        super(Layer, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.parent = parent
        self.p = parent.p
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)
        
        self.openSet = {}
        self.view = view
        self.currentChanged.connect(self.update)
        
        self.tmpView = None
        self.basePath = None
        
    def addView(self, fileInfo):
        path = fileInfo.absoluteFilePath()
        if path in self.openSet:
            self.setCurrentWidget(self.openSet[path])
            if self.tmpView is not None:
                self.closeTab(self.indexOf(self.tmpView))
            return
        tmp, name = os.path.split(path)
        
        if fileInfo.tmpView:
            try:
                if self.tmpView is None:
                    w = self.view(fileInfo, parent = self)
                    self.tmpView = w
                    self.setCurrentIndex(self.addTab(w, name))
                else:
                    self.closeTab(self.indexOf(self.tmpView))
                    w = self.view(fileInfo, parent=self)
                    self.tmpView = w
                    self.setCurrentIndex(self.addTab(w, name))
                return
            except:
                return

        if self.tmpView is not None:
            self.closeTab(self.indexOf(self.tmpView))
            
        w = self.view(fileInfo, parent=self)
        self.setCurrentIndex(self.addTab(w, name))
        self.openSet[path] = w
        
    def closeTab (self, currentIndex):
        w = self.widget(currentIndex)
        w.close()


class LayerWindow(QStackedWidget):
    
    def __init__(self, view, parent=None):
        super(LayerWindow, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.p = parent.p
        self.view = view
        self.layerSet = {}
        
    def addLayer(self, s):
        tab = Layer(s, self.view, self)
        self.layerSet[s] = tab
        self.addWidget(tab)
        
    def setLayer(self, s):
        w = self.layerSet[s]
        self.setCurrentWidget(w)
        
    def removeLayer(self, s):
        w = self.layerSet[s]
        del self.layerSet[s]
        w.deleteLater()
        self.removeWidget(w)
        
    def openView(self,  fileInfo):
        fileInfo.tmpView = False
        self.currentWidget().addView(fileInfo)

    def treeActivated(self, fileInfo):
        fileInfo.tmpView = False
        self.currentWidget().addView(fileInfo)

    def treeCurrentChanged(self, fileInfo):
        fileInfo.tmpView = True
        self.currentWidget().addView(fileInfo)


class View (QMainWindow):
    def __init__(self, fileInfo, parent = None):
        super(View, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.__version__ = '0.0.0'
        
        self.path = fileInfo.absoluteFilePath()

        self.fileInfo = fileInfo

        self.parent = parent
        self.p = parent.p
        self.dirty = False
        self.filename = None
        self.printer = None

        self.status = self.statusBar()
        self.status.setSizeGripEnabled(False)
        
        self.menubar = self.menuBar()

    def addActions(self, target, actions):

        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def closeEvent(self, event):
        if self.okToContinue():
            if self.fileInfo.tmpView and self.parent.tmpView is self:
                self.parent.tmpView = None
            
            currentIndex = self.parent.indexOf(self)
            
            if not self.fileInfo.tmpView:
                del self.parent.openSet[self.path]
            self.parent.removeTab(currentIndex)
            self.deleteLater()
            
        else:
            event.ignore()

    def setDirty(self, dirty = True):
        if self.fileInfo.tmpView:
            self.parent.tmpView = None
        self.dirty = dirty
        if self.fileInfo.tmpView and dirty:
            self.fileInfo.tmpView = False
            self.parent.tmpView = None
            self.parent.openSet[self.fileInfo.absoluteFilePath()] = self
            
    def okToContinue(self):
        
        if self.dirty:
            
            reply = QMessageBox.question(self, 'Unsaved Changed', 'Save unsaved changed?', QMessageBox.Yes| QMessageBox.No|QMessageBox.Cancel)
            
            if reply == QMessageBox.Cancel:
                return False
                
            elif reply == QMessageBox.Yes:
                self.fileSave()                
        return True                                               

    def isDirty(self):
        return self.dirty
        
    def fileSave(self):
        pass
