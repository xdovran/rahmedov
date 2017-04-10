import os

from PyQt5.QtWidgets import QAction

from gui.window import LayerWindow, View

#import cfg.step

# TODO:
# 1. Quickly navigating to different related files inside the current 
#    config and other condigs in a current project and compare/copy between them 
# 2. Autocompletion and  Automatic code generation 
# 3. Refactoring, Renaming affects dependencies 
# 4. Warning-as-you-type and detecting errors
# 5. Hovering over something to see the docs and usefull info
# 6. Runtime error and other info from cluster info


class MainWindow(View):
    def __init__(self, fileInfo, parent=None):
        super(MainWindow, self).__init__(fileInfo, parent)
        from . import editor as e
        self.center = e.GenericEditor(self)
        self.setCentralWidget(self.center)

        self.initAction()
        self.initMenubar()        

    def initAction(self):
       
        self.openAction = QAction("Open...", self)
        self.openAction.setStatusTip("Open existing document")
        self.openAction.setShortcut("Ctrl+O")
        #self.openAction.triggered.connect(self.center.openView)

        self.saveAction = QAction("Save", self)
        self.saveAction.setStatusTip("Save document")
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.triggered.connect(self.center.save)

        self.saveAsAction = QAction("Save as ...",self)
        self.saveAsAction.setStatusTip("Save document as")
        self.saveAsAction.setShortcut("Ctrl+Shift+S")
        self.saveAsAction.triggered.connect(self.center.save_as)

        self.printAction = QAction("Print document",self)
        self.printAction.setStatusTip("Print document")
        self.printAction.setShortcut("Ctrl+P")
        self.printAction.triggered.connect(self.center.printHandler)

        self.previewAction = QAction("Page Setup...",self)
        self.previewAction.setStatusTip("Preview page before printing")
        self.previewAction.setShortcut("Ctrl+Shift+P")
        self.previewAction.triggered.connect(self.center.preview)

        self.exitAction = QAction("Close",self)
        self.exitAction.setStatusTip("Exit the Editor")
        self.exitAction.setShortcut("Ctrl+Q")
        self.exitAction.triggered.connect(self.center.close)

        self.findAction = QAction("Find and replace",self)
        self.findAction.setStatusTip("Find and replace words in your document")
        self.findAction.setShortcut("Ctrl+F")
        self.findAction.triggered.connect(self.find_and_replace)        

        self.cutAction = QAction("Cut",self)
        self.cutAction.setStatusTip("Delete and copy text to clipboard")
        self.cutAction.setShortcut("Ctrl+X")
        self.cutAction.triggered.connect(self.center.cut)

        self.copyAction = QAction("Copy",self)
        self.copyAction.setStatusTip("Copy text to clipboard")
        self.copyAction.setShortcut("Ctrl+C")
        self.copyAction.triggered.connect(self.center.copy)        

        self.pasteAction = QAction("Paste",self)
        self.pasteAction.setStatusTip("Paste text from clipboard")
        self.pasteAction.setShortcut("Ctrl+V")
        self.pasteAction.triggered.connect(self.center.paste)
        
        self.undoAction = QAction("Undo",self)
        self.undoAction.setStatusTip("Undo last action")
        self.undoAction.setShortcut("Ctrl+Z")
        self.undoAction.triggered.connect(self.center.undo)

        self.redoAction = QAction("Redo",self)
        self.redoAction.setStatusTip("Redo last undone thing")
        self.redoAction.setShortcut("Ctrl+Y")
        self.redoAction.triggered.connect(self.center.redo)       
        
        self.indentAction = QAction("Indent Area",self)
        self.indentAction.setShortcut("Ctrl+Tab")
        self.indentAction.triggered.connect(self.center.indent)

        self.dedentAction = QAction("Dedent Area",self)
        self.dedentAction.setShortcut("Shift+Tab")
        self.dedentAction.triggered.connect(self.center.dedent)
        
    def find_and_replace(self):
        pass
    
    def fileSave(self):
        self.center.save()

    def initMenubar(self):
        
        file_m = self.menubar.addMenu("File+")
        edit_m = self.menubar.addMenu("Edit")        
        view_m = self.menubar.addMenu("View")
        # Add the most important actions to the menubar
        
        file_m.addAction(self.openAction)
        file_m.addAction(self.saveAction)
        file_m.addAction(self.saveAsAction)
        file_m.addAction(self.printAction)
        file_m.addAction(self.previewAction)
        file_m.addAction(self.exitAction)

        edit_m.addAction(self.undoAction)
        edit_m.addAction(self.redoAction)
        edit_m.addAction(self.cutAction)
        edit_m.addAction(self.copyAction)
        edit_m.addAction(self.pasteAction)
        edit_m.addAction(self.findAction)

        statusbarAction = QAction("Statusbar",self)
        statusbarAction.setCheckable(True)
        statusbarAction.triggered.connect(self.toggleStatusbar)

        view_m.addAction(statusbarAction)

    def on_text_changed(self):        
        return
        if self.editorLayer.currentIndex() == 0 and not self.firstView:
            t = TxtView(parent = self)
            t.textChanged.connect(self.on_text_changed)

            self.editorLayer.insertTab(0, t, 'New')
            self.editorLayer.setCurrentIndex(1)

            path, fil = os.path.split(self.open_files_0)            

            self.isDirty = True
            self.openSet[self.open_files_0] = self.editorLayer.currentWidget()            
        else:            
            self.editorLayer.currentWidget().isDirty = True    

    def toggleStatusbar(self):
        state = self.statusbar.isVisible()
        # Set the visibility to its inverse
        self.statusbar.setVisible(not state)

class TxtWindow(LayerWindow):
    def __init__(self, parent=None):
        LayerWindow.__init__(self, view=MainWindow, parent=parent)
        self.parent = parent
