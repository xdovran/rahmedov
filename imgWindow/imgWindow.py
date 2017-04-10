from gui.window import LayerWindow, View

from PyQt5 import QtGui, QtCore, QtWidgets, QtPrintSupport

import os
import platform
from . import helpform
from . import resizedlg
from . import imageLabel


class MainWindow(View):

    def __init__(self, fileInfo, parent=None):
        super(MainWindow, self).__init__(fileInfo, parent)
        self.__version__ = "1.0.0"
        self.center = imageLabel.GenericImage(self)
        self.setCentralWidget(self.center)

        self.dataObject = QtGui.QImage()

        self.windowName = 'ImgWindow'

        self.mirroredvertically = False
        self.mirroredhorizontally = False

        self.center.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        self.sizeLabel = QtWidgets.QLabel()

        self.sizeLabel.setFrameStyle(
            QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Sunken)
        
        self.status.addPermanentWidget(self.sizeLabel)

        self.status.showMessage("Ready", 5000)
        '''
        fileOpenAction = self.createAction("&Open...", self.fileOpen,
                QtGui.QKeySequence.Open, "fileopen",
                "Open an existing image file")
        '''

        fileSaveAction = QtWidgets.QAction('&Save', self)
        fileSaveAction.triggered.connect(self.fileSave)
        fileSaveAction.setShortcut(QtGui.QKeySequence.Save)
        fileSaveAction.setToolTip("Save the image")

        fileSaveAsAction = QtWidgets.QAction('Save &As...', self)
        fileSaveAsAction.triggered.connect(self.fileSaveAs)
        fileSaveAsAction.setToolTip("Save the image using a new name")

        filePrintAction = QtWidgets.QAction('&Print', self)
        filePrintAction.triggered.connect(self.filePrint)
        filePrintAction.setShortcut(QtGui.QKeySequence.Print)
        filePrintAction.setToolTip("Print the image")

        fileQuitAction = QtWidgets.QAction('&Quit', self)
        fileQuitAction.triggered.connect(self.close)
        fileQuitAction.setShortcut("Ctrl+Q")
        fileQuitAction.setToolTip("Close the application")

        editInvertAction = QtWidgets.QAction('&Invert', self)
        editInvertAction.toggled.connect(self.editInvert)
        editInvertAction.setShortcut("Ctrl+I")
        editInvertAction.setToolTip("Invert the image's colors")
        editInvertAction.setCheckable(True)

        editSwapRedAndBlueAction = QtWidgets.QAction('Sw&ap Red and Blue', self)
        editSwapRedAndBlueAction.toggled.connect(self.editSwapRedAndBlue)
        editSwapRedAndBlueAction.setShortcut("Ctrl+A")
        editSwapRedAndBlueAction.setToolTip("Invert the image's colors")
        editSwapRedAndBlueAction.setCheckable(True)

        editZoomAction = QtWidgets.QAction('&Zoom', self)
        editZoomAction.triggered.connect(self.editZoom)
        editZoomAction.setShortcut("Alt+Z")
        editZoomAction.setToolTip("Zoom the image")

        editResizeAction = QtWidgets.QAction('&Resize...', self)
        editResizeAction.triggered.connect(self.editResize)
        editResizeAction.setShortcut("Ctrl+R")
        editResizeAction.setToolTip("Resize the image")

        mirrorGroup = QtWidgets.QActionGroup(self)

        editUnMirrorAction = QtWidgets.QAction('&Unmirror', self)
        editUnMirrorAction.toggled.connect(self.editUnMirror)
        editUnMirrorAction.setShortcut("Ctrl+U")
        editUnMirrorAction.setToolTip("Unmirror the image")
        editUnMirrorAction.setCheckable(True)

        mirrorGroup.addAction(editUnMirrorAction)

        editMirrorHorizontalAction = QtWidgets.QAction('Mirror &Horisontal ', self)
        editMirrorHorizontalAction.toggled.connect(self.editMirrorHorizontal)
        editMirrorHorizontalAction.setShortcut("Ctrl+H")
        editMirrorHorizontalAction.setToolTip("Horizontally mirror the image")
        editMirrorHorizontalAction.setCheckable(True)

        mirrorGroup.addAction(editMirrorHorizontalAction)


        editMirrorVerticalAction = QtWidgets.QAction('Mirror &Vertically', self)
        editMirrorVerticalAction.toggled.connect(self.editMirrorVirtical)
        editMirrorVerticalAction.setShortcut("Ctrl+V")
        editMirrorVerticalAction.setToolTip("Vertically mirror the image")
        editMirrorVerticalAction.setCheckable(True)


        mirrorGroup.addAction(editMirrorVerticalAction)

        editUnMirrorAction.setChecked(True)

        helpAboutAction = QtWidgets.QAction('&Acout Image Changer')
        helpAboutAction.triggered.connect(self.helpAbout)

        helpAboutAction = QtWidgets.QAction('&Help')
        helpAboutAction.triggered.connect(self.helpHelp)
        helpAboutAction.setShortcut(QtCore.QKeySequence.HelpContents)

        self.fileMenu = self.menuBar().addMenu("&File")

        self.fileMenuActions = (
                fileSaveAction, fileSaveAsAction, None,
                filePrintAction, fileQuitAction)

        self.addActions(self.fileMenu, self.fileMenuActions)

        editMenu = self.menuBar().addMenu("&Edit")

        self.addActions(editMenu, (editInvertAction,
                editSwapRedAndBlueAction, editZoomAction,
                editResizeAction))

        mirrorMenu = editMenu.addMenu(QtGui.QIcon(":/editmirror.png"),
                                      "&Mirror")

        self.addActions(mirrorMenu, (editUnMirrorAction,
                editMirrorHorizontalAction, editMirrorVerticalAction))

        helpMenu = self.menuBar().addMenu("&Help")

        self.addActions(helpMenu, (helpAboutAction, helpHelpAction))        
        
        self.zoomSpinBox = QtWidgets.QSpinBox()
        self.zoomSpinBox.setRange(1, 400)
        self.zoomSpinBox.setSuffix(" %")
        self.zoomSpinBox.setValue(100)
        self.zoomSpinBox.setToolTip("Zoom the image")
        self.zoomSpinBox.setStatusTip(self.zoomSpinBox.toolTip())
        self.zoomSpinBox.setFocusPolicy(QtCore.Qt.NoFocus)

        self.zoomSpinBox.valueChanged[int].connect(self.showImage)
        
        self.status.addPermanentWidget(self.zoomSpinBox)

        self.addActions(self.center, (editInvertAction,
                editSwapRedAndBlueAction, editUnMirrorAction,
                editMirrorVerticalAction, editMirrorHorizontalAction))

        self.resetableActions = ((editInvertAction, False),
                                 (editSwapRedAndBlueAction, False),
                                 (editUnMirrorAction, True))
        
        self.loadFile(self.path) 

    def updateStatus(self, message):

        self.status.showMessage(message, 5000)        
        
        if self.filename is not None:
            self.setWindowTitle("Image Changer - %s[*]" % \
                                os.path.basename(self.filename))

        elif not self.dataObject.isNull():
            self.setWindowTitle("Image Changer - Unnamed[*]")

        else:
            self.setWindowTitle("Image Changer[*]")

        self.setWindowModified(self.dirty)
        
        if self.fileInfo['tmpView']:
            self.parent.tmpView = None

    def loadFile(self, fname=None):
        if fname is None:
            action = self.sender()
            if isinstance(action, QtWidgets.QAction):
                fname = action.data().toString()
                if not self.okToContinue():
                    return
            else:
                return
        if fname:
            self.filename = None
            image = QtGui.QImage(fname)
            if image.isNull():
                message = "Failed to read %s" % fname
            else:
                self.addRecentFile(fname)
                self.dataObject = QtGui.QImage()
                for action, check in self.resetableActions:
                    action.setChecked(check)
                self.dataObject = image
                self.filename = fname
                self.showImage()
                self.setDirty(False)
                self.sizeLabel.setText("%d x %d" % (
                            image.width(), image.height()))
                message = "Loaded %s" % os.path.basename(fname)
            self.updateStatus(message)


    def fileSave(self):
        if self.dataObject.isNull():
            return
        if self.filename is None:
            self.fileSaveAs()
        else:
            if self.dataObject.save(self.filename, None):
                self.updateStatus("Saved as %s" % self.filename)
                self.setDirty(False)
            else:
                self.updateStatus("Failed to save %s" % self.filename)


    def fileSaveAs(self):
        if self.dataObject is None:
            return
        fname = self.filename if self.filename is not None else "."
        formats = ["*.%s" % format.lower() \
                   for format in QtGui.QImageWriter.supportedImageFormats()]
        fname = QtWidgets.QFileDialog.getSaveFileName(self,
                        "Image Changer - Save Image", fname,
                        "Image files (%s)" % " ".join(formats))
        if fname:
            if "." not in fname:
                fname += ".png"
            self.addRecentFile(fname)
            self.filename = fname
            self.fileSave()


    def filePrint(self):
        if self.dataObject is None:
            return
        if self.printer is None:
            self.printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
            self.printer.setPageSize(QtPrintSupport.QPrinter.Letter)
        form = QtPrintSupport.QPrintDialog(self.printer, self)
        if form.exec_():
            painter = QtPrintSupport.QPainter(self.printer)
            rect = painter.viewport()
            size = self.dataObject.size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(),
                                size.height())
            painter.drawImage(0, 0, self.dataObject)


    def editInvert(self, on):
        if self.dataObject.isNull():
            return
        self.dataObject.invertPixels()
        self.showImage()
        self.setDirty(True)        
        self.updateStatus("Inverted" if on else "Uninverted")


    def editSwapRedAndBlue(self, on):
        if self.dataObject.isNull():
            return
        self.dataObject = self.dataObject.rgbSwapped()
        self.showImage()
        
        self.setDirty(True)
        self.updateStatus("Swapped Red and Blue" \
                if on else "Unswapped Red and Blue")


    def editUnMirror(self, on):
        if self.dataObject.isNull():
            return
        if self.mirroredhorizontally:
            self.editMirrorHorizontal(False)
        if self.mirroredvertically:
            self.editMirrorVertical(False)


    def editMirrorHorizontal(self, on):
        if self.dataObject.isNull():
            return
        self.dataObject = self.dataObject.mirrored(True, False)
        self.showImage()
        self.mirroredhorizontally = not self.mirroredhorizontally
        self.setDirty(True)
        self.updateStatus("Mirrored Horizontally" \
                if on else "Unmirrored Horizontally")


    def editMirrorVertical(self, on):
        if self.dataObject.isNull():
            return
        self.dataObject = self.dataObject.mirrored(False, True)
        self.showImage()
        self.mirroredvertically = not self.mirroredvertically
        self.setDirty(True)
        self.updateStatus("Mirrored Vertically" \
                if on else "Unmirrored Vertically")


    def editZoom(self):
        if self.dataObject.isNull():
            return
        percent, ok = QtWidgets.QInputDialog.getInteger(self,
                "Image Changer - Zoom", "Percent:",
                self.zoomSpinBox.value(), 1, 400)
        if ok:
            self.zoomSpinBox.setValue(percent)


    def editResize(self):
        if self.dataObject.isNull():
            return
        form = resizedlg.ResizeDlg(self.dataObject.width(),
                                   self.dataObject.height(), self)
        if form.exec_():
            width, height = form.result()
            if width == self.dataObject.width() and \
               height == self.dataObject.height():
                self.status.showMessage(
                        "Resized to the same size", 5000)
            else:
                self.dataObject = self.dataObject.scaled(width, height)
                self.showImage()
                self.setDirty(True)
                size = "%d x %d" % (self.dataObject.width(),
                                    self.dataObject.height())
                self.sizeLabel.setText(size)
                self.updateStatus("Resized to %s" % size)


    def showImage(self, percent=None):
        
        if self.dataObject.isNull():
            return
        if percent is None:
            percent = self.zoomSpinBox.value()
            
        factor = percent / 100.0
        width = self.dataObject.width() * factor
        height = self.dataObject.height() * factor
        image = self.dataObject.scaled(width, height, QtCore.Qt.KeepAspectRatio)
        
        self.center.setPixmap(QtGui.QPixmap.fromImage(image))

    def helpAbout(self):
        QtWidgets.QMessageBox.about(self, "About Image Viewer",
                """<b>Image Viewer</b> v %s
                <p>Model Engine; 2016 QuantLab LLC. 
                All rights reserved.
                <p>This application can be used to perform
                simple image manipulations.
                <p>Python %s - Qt %s - PyQt %s 
                on %s""" % (self.__version__, platform.python_version(),
                QtCore.QT_VERSION_STR, QtCore.PYQT_VERSION_STR, platform.system()))


    def helpHelp(self):
        form = helpform.HelpForm("index.html", self)
        form.show()

class ImgWindow(LayerWindow):
    def __init__(self, parent = None):
        super(ImgWindow, self).__init__(view=MainWindow, parent=parent)
        self.parent = parent

