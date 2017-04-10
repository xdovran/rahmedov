import os
import subprocess
import datetime
import shutil

from PyQt5.QtWidgets import (
    QAction,
    QToolBar,
    QComboBox,
    QLineEdit,
    QSizePolicy,
    QMenu,
    QPushButton,
    QFileDialog,
    QToolButton,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QTableWidget,
    QCheckBox,
    QGroupBox,
    QDialogButtonBox,
    QListWidget,
    QStackedLayout,
    QWidget,
    QRadioButton,
)
from PyQt5.QtGui import (
    QIcon,
    QPixmap,
)
from PyQt5.QtCore import (
    pyqtSlot,
    pyqtSignal,
    QAbstractListModel,
    Qt,
    QThread,
    QModelIndex,
)


#import resource_files
class Model(QAbstractListModel):
    def __init__(self, layerList=[], parent=None):
        super(Model, self).__init__(parent)
        self.layerList = layerList
        self.parent = parent

    def rowCount(self, parent):
        return len(self.layerList)

    def data(self, index, role):
        if role == Qt.EditRole:
            return self.layerList[index.row()]
        if role == Qt.DisplayRole:
            row = index.row()
            return self.layerList[row]

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled
        
    def setData(self, index, v, role=Qt.EditRole):
        if role == Qt.EditRole:
            v = self.validPath(v)
            if v:
                row = index.row()
                if row == -1:
                    self.layerList.append(v)
                else:
                    self.layerList.insert(row, v)
                self.dataChanged.emit(index, index)
                return True
            return False

    def add(self, s):
        s = self.validPath(s)
        if not s:
            return
        try:
            i = self.layerList.index(s)
        except:
            self.layerList.append(s)
            self.layerList.sort()
            i = self.layerList.index(s)
        index = self.index(i)
        self.dataChanged.emit(index, index)
        self.parent.layerBox.setCurrentIndex(i)

        self.defaultPath, _ = os.path.split(s)
        
    def insertRows(self, position, rows, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        self.endInsertRows()
        return True
        
    def removeRows(self, position, rows, parent=QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        
        for i in range(rows):
            value = self.layerList[position]
            self.layerList.remove(value)
        self.endRemoveRows()
        return True
        
    def validPath(self, path):

        while len(path) > 7:
            try:
                dirPath, name = os.path.split(path)
                y = int(name[:4])
                m = int(name[4:6])
                d = int(name[6:8])
                datetime.datetime(year=y, month=m, day=d)
                if self.validConfig(path):
                    return path
            except:
                pass
            path = dirPath

        return path

    def validConfig(self, path):
        '''
        check if we have configuration files inside
        of the path
        '''
        validConfig = True

        config = os.path.join(path, 'config')

        return True


class ToolBar(QToolBar):
    def __init__(self, parent):
        super(ToolBar, self).__init__(parent)
        
        self.p = parent

        self.explorer = parent.explorer
        self.window = parent.window
        self.layerSet = set()
        
        self.initAction()
        self.initToolbar()
        
        self.defaultPath = self.p.guiPath
        
    def initToolbar(self):
        self.layerBox = QComboBox(self)
        self.model = Model(parent=self)
        
        self.layerBox.setModel(self.model)
        self.layerBox.setStyleSheet('QComboBox {font : bold 14px;}')
        
        self.layerBox.setEditable(True)
        self.layerBox.setEnabled(True)
        
        self.layerBox.setInsertPolicy(QComboBox.InsertAlphabetically)        
        
        self.layerEditor = QLineEdit(self.layerBox)
        self.layerBox.setLineEdit(self.layerEditor)
        
        self.layerBox.activated[str].connect(self.activatedS)
        self.layerBox.activated[int].connect(self.activated)
        self.layerBox.highlighted[str].connect(self.highlightedS)
        self.layerBox.highlighted[int].connect(self.highlighted)
        self.layerBox.currentIndexChanged[str].connect(self.layerIndexChangedS)
        self.layerBox.currentIndexChanged[int].connect(self.layerIndexChanged)
        self.layerBox.editTextChanged[str].connect(self.editTextChanged)
        
        self.layerBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.subMenu = QMenu(self)
        self.subMenu.addAction(self.fullScreenAction)
        self.subMenu.addAction(self.windowSplitAction)
        self.subMenu.addAction(self.screenshotAction)
        self.subMenu.addAction(self.settingAction)
        
        self.pushbutton = QToolButton(self)
        self.pushbutton.setIcon(QIcon(os.path.join(self.p.appPath, 'svg', 'toolbar_list.png')))

        self.pushbutton.setMenu(self.subMenu)
        self.pushbutton.setPopupMode(QToolButton.InstantPopup)
        self.pushbutton.setStyleSheet('QToolButton::menu-indicator{image: none}')

        self.setOrientation(Qt.Horizontal)
        
        self.bg = {}
        
        for x in sorted(self.window.windowList):
            button = QToolButton(self)
            button.setText(x)
            button.setStyleSheet("QToolButton {font: bold 14px};")

            self.bg[x] = button
            if x == 'Editor':
                button.clicked.connect(self.setEditorWindow)
            elif x == 'Image':
                button.clicked.connect(self.setImageWindow)

            self.addWidget(button)
            
        self.setWindow('Editor')
        
        self.addAction(self.addLocationAction)
        self.addAction(self.duplicateAction)
        self.addWidget(self.layerBox)
        self.addAction(self.removeAction)
        self.addWidget(self.pushbutton)
        self.model.add(self.p.root)

    def setEditorWindow(self):
        self.setWindow('Editor')

    def setImageWindow(self):
        self.setWindow('Image')

    def setWindow(self, name):
        self.window.setWindow(name)
        for x in self.bg:
            if x == name:
                self.bg[x].setStyleSheet('QToolButton {background-color: orange; color:black}')
            else:
                self.bg[x].setStyleSheet('QToolButton {background-color: #302F2F;')

    @pyqtSlot(int)
    def activated(self, i):
        pass

    @pyqtSlot(str)
    def activatedS(self, s):
        pass

    @pyqtSlot(int)
    def highlighted(self, i):
        pass

    @pyqtSlot(str)
    def highlightedS(self, s):
        pass

    def editTextChanged(self, s):
        pass

    @pyqtSlot(str)
    def layerIndexChangedS(self, s):
        if not os.path.isdir(s):
            return
        if s not in self.layerSet:
            self.addLayer(s)
            self.layerSet.add(s)
        self.window.setLayer(s)
        self.explorer.setLayer(s)

    def layerIndexChanged(self, i):
        pass
    
    def addLayer(self, s):
        self.window.addLayer(s)
        self.explorer.addLayer(s)
        
    def setEditor(self):
        self.p.window.setEditor()    
                
    def initAction(self):
        self.editorAction = QAction(
            QIcon(''), 'Editor', self)
        self.editorAction.triggered.connect(self.setEditor)

        # self.editorAction.triggered.connect(self.setEditor)

        self.duplicateAction = QAction(
            QIcon(os.path.join(self.p.appPath, 'svg', 'tool_duplicate.png')), 'Duplicate Current', self)
        self.duplicateAction.triggered.connect(self.duplicate)        
        
        self.downloadAction = QAction(
            QIcon(''), 'Download and add', self)
        self.downloadAction.triggered.connect(self.download)
        

        self.fullScreenAction = QAction(
            QIcon(''), 'Full Screen', self)
        self.fullScreenAction.triggered.connect(self.fullScreen)
        
        self.windowSplitAction = QAction(
            QIcon(''), 'Window Split', self)
        self.windowSplitAction.triggered.connect(self.windowSplit)
        
        self.screenshotAction = QAction(
            QIcon(''), 'Screen Shot', self)
        self.screenshotAction.triggered.connect(self.screenshot)
        
        self.settingAction = QAction(
            QIcon(''), 'Setting', self)
        self.settingAction.triggered.connect(self.setting)

        self.addLocationAction = QAction(
            QIcon(os.path.join(self.p.appPath, 'svg', 'toolbar_plus.png')), 'Open Location', self)
        self.addLocationAction.triggered.connect(self.addLocation)
        
        self.removeAction = QAction(
            QIcon(os.path.join(self.p.appPath, 'svg', 'toolbar_minus.png')), 'Remove Current Location', self)
        self.removeAction.triggered.connect(self.remove)

    def fullScreen(self):
        if self.p.isFullScreen():
            self.p.showMaximized()
            self.fullScreenAction.setIcon(QIcon(':/full.png'))
        else:
            self.fullScreenAction.setIcon(QIcon(':/exitfull.png'))
            self.p.showFullScreen()

    def download(self):
        ''' copy directory list from one location and paste it to new location
        '''
        # default path of copy destination
        if self.layerBox.count() > 0:
            # if we have directory in the system choose path to the current 
            # directory as a default path
            defaultPath = str(self.layerBox.currentText())
        else:
            # otherwise choose a work directory from where script is running
            defaultPath = self.meGuiPath

        defaultDestination, _ = os.path.split(defaultPath)

        newLocation = str(QFileDialog.getExistingDirectory(self, 'Select Directory to copy',  defaultDestination))

        if (newLocation):
            dialog = CopyDlg(newLocation,  self)
            if dialog.exec_():
                fromPathList = []
                for dir in dialog.dirs:
                    if dialog.dirs[dir].isChecked():
                       fromPathList.append(os.path.join(newLocation, dir))
        else:
            return
                        
        toPath = str(QFileDialog.getExistingDirectory(self, 'Select Directory to copy',  defaultDestination))

        self.cp(ar, newLocation)

    def screenshot(self):
        # if we want to save whole desktop we can do:
        # QtGui.QPixmap.grabWindow(
        #   QtGui.QApplication.desktop().winId()).save(
        #       R'C:\src\me_ui\ModelEngine\bin.x64\pyqlrio\screenshot.png', 'png')
        fileName = QFileDialog.getSaveFileName(self,"Save File",
                            ".", "Images (*.png)");
        if fileName:
            QPixmap.grabWidget(self.p).save(fileName)

    def cp(self, fromPathList, toPath):         
        th = CopyThread(fromPathList, toPath)
        th.update.connect(self.model.add)
        th.start()

    def windowSplit(self):
        if self.explorer.isHidden():
            self.explorer.setHidden(False)
            self.windowSplitAction.setIcon(QIcon(":/window.png"))
        else:
            self.explorer.setHidden(True)
            self.windowSplitAction.setIcon(QIcon(":/window-split.png"))

    def setting(self):
        self.dialog = PreferenceDialog(self)
        self.dialog.show()

    def addLocation(self):
        newLocation = QFileDialog.getExistingDirectory(
            self, 'Select Directory To add to current Project', self.defaultPath)

        if (newLocation): 
            self.model.add(newLocation)
            
    def remove(self):
        i = self.layerBox.currentIndex() 
        dirPath = self.layerBox.itemText(i)

        if i > -1:
            self.explorer.removeLayer(dirPath)
            self.window.removeLayer(dirPath)            
            self.layerSet.remove(dirPath)
            self.model.removeRows(i, 1)
            
 
    def download(self):
        ''' copy directory list from one location and paste it to new location
        '''
        # default path of copy destination
        if self.layerBox.count() > 0:
            # if we have directory in the system choose path to the current 
            # directory as a default path
            defaultPath = self.layerBox.currentText()
        else:
            # otherwise choose a work directory from where script is running
            defaultPath = self.p.guiPath

        defaultDestination, _ = os.path.split(defaultPath)

        newLocation = QFileDialog.getExistingDirectory(
            self, 'Select Directory to copy',  defaultDestination)

        if (newLocation):
            dialog = DuplicateDialog(self)
            if dialog.exec_():
                fromPathList = []
                for dir in dialog.dirs:
                    if dialog.dirs[dir].isChecked():
                       fromPathList.append(os.path.join(newLocation, dir))
        else:
            return
                
        toPath = str(QFileDialog.getExistingDirectory(
                self, 'Select Directory to copy',  defaultDestination))
        self.cp(fromPathList, toPath)



    def duplicate(self):
        path = False

        if self.layerBox.count() > 0:
            path = self.layerBox.currentText()
        else:
            path = self.p.appPath

        if not path:
            return

        dialog = DuplicateDialog(self)

        dialog.show()
    
    def validLocation(self, rootPath):
        # Is rootPath valid directory i.e directory with valid 
        # config and bin.x64 subdirectories 
        rootPath = rootPath
        # see if we have a config directory
        config = os.path.join(rootPath, 'config')  
        if not os.path.isdir(config):
            return False
        return True


class CopyThread(QThread):
    '''creates thread that copies list of directory trees to another location'''

    update = pyqtSignal(str)

    def __init__(self, fromPathList, toPath):
        QThread.__init__(self)        
        self.toPath = toPath
        self.fromPathList = fromPathList # list of paths 
    def __del__(self):
        self.wait()

    def run(self):        
        for dirPath in self.fromPathList:

            _, dirName = os.path.split(dirPath)
            to = os.path.join(self.toPath, dirName)

            shutil.copytree(dirPath, to)

        self.update.emit(self.toPath)


class PreferenceDialog(QDialog):
    def __init__(self, parent=None):
        super(PreferenceDialog, self).__init__(parent)
        self.createAppearancePage()
        self.createWebBrowserPage()
        self.createMailAndsPage()
        self.createAdvancedPage()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok |
                                     QDialogButtonBox.Cancel)

        self.listWidget = QListWidget()
        self.listWidget.addItem(self.tr("Appearance"))
        self.listWidget.addItem(self.tr("Web Browser"))
        self.listWidget.addItem(self.tr("Mail & s"))
        self.listWidget.addItem(self.tr("Advanced"))

        stackedLayout = QStackedLayout()
        stackedLayout.addWidget(self.appearancePage)
        stackedLayout.addWidget(self.webBrowserPage)
        stackedLayout.addWidget(self.mailAndsPage)
        stackedLayout.addWidget(self.advancedPage)
        self.listWidget.currentRowChanged[int].connect(
                stackedLayout.setCurrentIndex)

        mainLayout = QGridLayout()
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 3)
        mainLayout.addWidget(self.listWidget, 0, 0)
        mainLayout.addLayout(stackedLayout, 0, 1)
        mainLayout.addWidget(buttonBox, 1, 0, 1, 2)
        self.setLayout(mainLayout)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setWindowTitle(self.tr("Preferences"))
        self.listWidget.setCurrentRow(0)

    def createAppearancePage(self):
        self.appearancePage = QWidget(self)

        openGroupBox = QGroupBox(self.tr("Open at startup"))
        webBrowserCheckBox = QCheckBox(self.tr("Web browser"))
        mailEditorCheckBox = QCheckBox(self.tr("Mail editor"))
        sgroupCheckBox = QCheckBox(self.tr("sgroups"))

        toolbarsGroupBox = QGroupBox(self.tr("Show toolbars as"))
        picturesAndTextRadioButton = QRadioButton(self.tr("Pictures and text"))
        picturesOnlyRadioButton = QRadioButton(self.tr("Pictures only"))
        textOnlyRadioButton = QRadioButton(self.tr("Text only"))

        tooltipsCheckBox = QCheckBox(self.tr("Show tooltips"))
        webSiteIconsCheckBox = QCheckBox(self.tr("Show web site icons"))
        resizeImagesCheckBox = QCheckBox(self.tr("Resize large images to "
                                                "fit in the window"))

        openLayout = QVBoxLayout()
        openLayout.addWidget(webBrowserCheckBox)
        openLayout.addWidget(mailEditorCheckBox)
        openLayout.addWidget(sgroupCheckBox)
        openGroupBox.setLayout(openLayout)

        toolbarsLayout = QVBoxLayout()
        toolbarsLayout.addWidget(picturesAndTextRadioButton)
        toolbarsLayout.addWidget(picturesOnlyRadioButton)
        toolbarsLayout.addWidget(textOnlyRadioButton)
        toolbarsGroupBox.setLayout(toolbarsLayout)

        pageLayout = QVBoxLayout()
        #pageLayout.setMargin(0)
        pageLayout.addWidget(openGroupBox)
        pageLayout.addWidget(toolbarsGroupBox)
        pageLayout.addWidget(tooltipsCheckBox)
        pageLayout.addWidget(webSiteIconsCheckBox)
        pageLayout.addWidget(resizeImagesCheckBox)
        pageLayout.addStretch()
        self.appearancePage.setLayout(pageLayout)

        webBrowserCheckBox.setChecked(True)
        mailEditorCheckBox.setChecked(True)
        picturesAndTextRadioButton.setChecked(True)
        tooltipsCheckBox.setChecked(True)
        webSiteIconsCheckBox.setChecked(True)

    def createWebBrowserPage(self):

        self.webBrowserPage = QWidget(self)

        displayGroupBox = QGroupBox(self.tr("Display on startup"))
        blankRadioButton = QRadioButton(self.tr("Blank page"))
        homeRadioButton = QRadioButton(self.tr("Blank page"))
        lastRadioButton = QRadioButton(self.tr("Last page visited"))

        homeGroupBox = QGroupBox(self.tr("Home Page"))
        locationLabel = QLabel(self.tr("Location:"))
        locationLineEdit = QLineEdit()

        webButtonsGroupBox = QGroupBox(self.tr("Select the buttons you want "
                                              "in the toolbar"))
        bookmarksCheckBox = QCheckBox(self.tr("Bookmarks"))
        goCheckBox = QCheckBox(self.tr("Go"))
        homeCheckBox = QCheckBox(self.tr("Home"))
        searchCheckBox = QCheckBox(self.tr("Search"))
        printCheckBox = QCheckBox(self.tr("Print"))

        displayLayout = QVBoxLayout()
        displayLayout.addWidget(blankRadioButton)
        displayLayout.addWidget(homeRadioButton)
        displayLayout.addWidget(lastRadioButton)
        displayGroupBox.setLayout(displayLayout)

        homeLayout = QHBoxLayout()
        homeLayout.addWidget(locationLabel)
        homeLayout.addWidget(locationLineEdit)
        homeGroupBox.setLayout(homeLayout)

        webButtonsLayout = QGridLayout()
        webButtonsLayout.addWidget(bookmarksCheckBox, 0, 0)
        webButtonsLayout.addWidget(goCheckBox, 1, 0)
        webButtonsLayout.addWidget(homeCheckBox, 2, 0)
        webButtonsLayout.addWidget(searchCheckBox, 0, 1)
        webButtonsLayout.addWidget(printCheckBox, 1, 1)
        webButtonsGroupBox.setLayout(webButtonsLayout)

        pageLayout = QVBoxLayout()
        #pageLayout.setMargin(0)
        pageLayout.addWidget(displayGroupBox)
        pageLayout.addWidget(homeGroupBox)
        pageLayout.addWidget(webButtonsGroupBox)
        pageLayout.addStretch()
        self.webBrowserPage.setLayout(pageLayout)

        homeRadioButton.setChecked(True)
        locationLineEdit.setText("http://www.trolltech.com/")
        bookmarksCheckBox.setChecked(True)
        homeCheckBox.setChecked(True)
        searchCheckBox.setChecked(True)
        printCheckBox.setChecked(True)

    def createMailAndsPage(self):

        self.mailAndsPage = QWidget(self)

        generalGroupBox = QGroupBox(self.tr("General settings"))
        confirmCheckBox = QCheckBox(self.tr("Warn when moving folders to "
                                           "the Trash"))
        rememberCheckBox = QCheckBox(self.tr("Remember the last selected "
                                            "message"))

        mailButtonsGroupBox = QGroupBox(self.tr("Select the buttons you "
                                               "want in the toolbar"))
        fileCheckBox = QCheckBox(self.tr("File"))
        nextCheckBox = QCheckBox(self.tr("Next"))
        stopCheckBox = QCheckBox(self.tr("Stop"))
        junkCheckBox = QCheckBox(self.tr("Junk"))

        generalLayout = QVBoxLayout()
        generalLayout.addWidget(confirmCheckBox)
        generalLayout.addWidget(rememberCheckBox)
        generalGroupBox.setLayout(generalLayout)

        mailButtonsLayout = QGridLayout()
        mailButtonsLayout.addWidget(fileCheckBox, 0, 0)
        mailButtonsLayout.addWidget(nextCheckBox, 1, 0)
        mailButtonsLayout.addWidget(stopCheckBox, 0, 1)
        mailButtonsLayout.addWidget(junkCheckBox, 1, 1)
        mailButtonsGroupBox.setLayout(mailButtonsLayout)

        pageLayout = QVBoxLayout()
        #pageLayout.setMargin(0)
        pageLayout.addWidget(generalGroupBox)
        pageLayout.addWidget(mailButtonsGroupBox)
        pageLayout.addStretch()
        self.mailAndsPage.setLayout(pageLayout)

        confirmCheckBox.setChecked(True)
        rememberCheckBox.setChecked(True)
        nextCheckBox.setChecked(True)
        junkCheckBox.setChecked(True)

    def createAdvancedPage(self):

        self.advancedPage = QWidget(self)

        featuresGroupBox = QGroupBox(self.tr("Features that help "
                                            "interpret web pages"))
        javaCheckBox = QCheckBox(self.tr("Enable Java"))
        ftpCheckBox = QCheckBox(self.tr("Use this email address for "
                                       "anonymous FTP:"))
        ftpLineEdit = QLineEdit()

        ftpCheckBox.toggled[bool].connect(
                ftpLineEdit.setEnabled)

        featuresLayout = QGridLayout()
        featuresLayout.addWidget(javaCheckBox, 0, 0, 1, 2)
        featuresLayout.addWidget(ftpCheckBox, 1, 0, 1, 2)
        featuresLayout.addWidget(ftpLineEdit, 2, 1)
        featuresGroupBox.setLayout(featuresLayout)

        pageLayout = QVBoxLayout()
        # pageLayout.setMargin(0)
        pageLayout.addWidget(featuresGroupBox)
        pageLayout.addStretch()
        self.advancedPage.setLayout(pageLayout)

        javaCheckBox.setChecked(True)
        ftpLineEdit.setEnabled(False)


class DuplicateDialog(QDialog):
    def __init__(self, parent=None):
        super(DuplicateDialog, self).__init__(parent)

        namedLabel = QLabel(self.tr("&Named:"))
        namedLineEdit = QLineEdit()
        namedLabel.setBuddy(namedLineEdit)

        lookInLabel = QLabel(self.tr("&Look in:"))
        lookInLineEdit = QLineEdit()
        lookInLabel.setBuddy(lookInLineEdit)

        subfoldersCheckBox = QCheckBox(self.tr("Include subfolders"))

        labels = []
        labels.append(self.tr("Name"))
        labels.append(self.tr("In Folder"))
        labels.append(self.tr("Size"))
        labels.append(self.tr("Modified"))

        tableWidget = QTableWidget()
        tableWidget.setColumnCount(4)
        tableWidget.setHorizontalHeaderLabels(labels)

        messageLabel = QLabel(self.tr("0 files found"))
        messageLabel.setFrameShape(QLabel.Panel)
        messageLabel.setFrameShadow(QLabel.Sunken)

        findButton = QPushButton(self.tr("&Find"))
        stopButton = QPushButton(self.tr("Stop"))
        closeButton = QPushButton(self.tr("Close"))
        helpButton = QPushButton(self.tr("Help"))

        closeButton.clicked.connect(self.close)

        leftLayout = QGridLayout()
        # (widget, row, column, rowSpan=1, columnSpan=1)
        leftLayout.addWidget(namedLabel, 0, 0)
        leftLayout.addWidget(namedLineEdit, 0, 1)
        leftLayout.addWidget(lookInLabel, 1, 0)
        leftLayout.addWidget(lookInLineEdit, 1, 1)
        leftLayout.addWidget(subfoldersCheckBox, 2, 0, 1, 2)
        leftLayout.addWidget(tableWidget, 3, 0, 1, 2)
        leftLayout.addWidget(messageLabel, 4, 0, 1, 2)

        rightLayout = QVBoxLayout()
        rightLayout.addWidget(findButton)
        rightLayout.addWidget(stopButton)
        rightLayout.addWidget(closeButton)
        # put any excess space between the Close button and the Help button
        rightLayout.addStretch()
        rightLayout.addWidget(helpButton)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(rightLayout)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Find Files or Folders"))
