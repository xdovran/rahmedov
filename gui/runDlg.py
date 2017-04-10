# -*- coding: utf-8 -*-


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import (
    QWidget,
    QDialog,
    QStackedWidget,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QCheckBox,
    QLabel,
    # QInputDialog,
    QSpinBox,
)
from contextlib import closing

import os
import subprocess

class StringListDlg(QDialog):

    def __init__(self, parent=None):

        super(StringListDlg, self).__init__(parent)

        self.path = parent.path
        self.cfgPath = parent.cfgPath

        self.name = 'Run: '

        self.stack = QStackedWidget(self)

        self.listWidget = QListWidget()
        self.listWidget.currentItemChanged.connect(self.setView)

        self.runconfig={
            'Default':
                {
                    'numCores':60,
                    'writeDates':True,
                    'cluster':True,
                    'ignoreCacheCheck':True,
                    'tag':'',
                    'step':'',
                }
        }


        self.runConfigDlg = {}

        for s in self.runConfig:
            self.listWidget.addItem(s)
            self.runConfigDlg[s] = RefitDlg(name=s, format = self.runConfig[s], parent = self)
            self.stack.addWidget(self.runConfigDlg[s])

        self.listWidget.setCurrentRow(0)        

        buttonLayout = QVBoxLayout()
        # New
        self.newButton = QPushButton('New')

        self.newButton.setFocusPolicy(Qt.NoFocus)
        buttonLayout.addWidget(self.newButton)
        self.newButton.clicked.connect(self.new)
        # Edit 
        self.editButton = QPushButton('Edit')

        self.editButton.setFocusPolicy(Qt.NoFocus)
        buttonLayout.addWidget(self.editButton)
        self.editButton.clicked.connect(self.edit)

        # Remove
        self.removeButton = QPushButton('Remove')

        self.removeButton.setFocusPolicy(Qt.NoFocus)
        buttonLayout.addWidget(self.removeButton)
        self.removeButton.clicked.connect(self.remove)
        # Save
        self.saveButton = QPushButton('Save')

        self.saveButton.setFocusPolicy(Qt.NoFocus)
        buttonLayout.addWidget(self.saveButton)
        self.saveButton.clicked.connect(self.save)

        # Save As
        self.saveAsButton = QPushButton('Save As')

        self.saveAsButton.setFocusPolicy(Qt.NoFocus)
        buttonLayout.addWidget(self.saveAsButton)
        self.saveAsButton.clicked.connect(self.saveAs)
        # Revert
        self.revertButton = QPushButton('Revert')

        self.revertButton.setFocusPolicy(Qt.NoFocus)
        buttonLayout.addWidget(self.revertButton)
        self.revertButton.clicked.connect(self.revert)
        # Run 
        self.runButton = QPushButton('Run')

        self.runButton.setFocusPolicy(Qt.NoFocus)
        buttonLayout.addWidget(self.runButton)
        self.runButton.clicked.connect(self.run)
        buttonLayout.addStretch()
        # Close
        self.closeButton = QPushButton('Close')

        self.closeButton.setFocusPolicy(Qt.NoFocus)
        buttonLayout.addWidget(self.closeButton)
        self.closeButton.clicked.connect(self.accept)
        
        layout = QHBoxLayout()
        layout.addWidget(self.stack)
        layout.addWidget(self.listWidget)
        layout.addLayout(buttonLayout)
        
        self.setLayout(layout)
        self.setWindowTitle("Edit {} List".format(self.name))

    def setView(self, i):
        s = str(i.text())
        self.stack.setCurrentWidget(self.runConfigDlg[s])
        self.setWindowTitle(s)
        
    def new(self):
        row = self.listWidget.currentRow()
        title = "Add {}".format(self.name)
        string, ok = QInputDialog.getText(self, title, title)
        if ok and string:
            s = str(string).strip()
            if s == 'Default':
                return
                

            self.listWidget.insertItem(row, s)            
            self.runConfigDlg[s] = RefitDlg(name = s, format = self.runConfig['Default'], parent = self)
            self.stack.addWidget(self.runConfigDlg[s])
            self.runConfig[s]  = self.runConfig['Default']

    def edit(self):
        row = self.listWidget.currentRow()
        item = self.listWidget.item(row)
        old = str(item.text()).strip()

        if item is not None:
            title = "Edit {}".format(self.name)
            string, ok = QInputDialog.getText(self, title, title,
                    QLineEdit.Normal, item.text())
            if ok and string:
                new = str(string).strip()
                if new == 'Default':
                    return

                item.setText(new)
                self.runConfigDlg[new] = self.runConfigDlg[old]
                self.runConfig[new] = self.runConfig[old]
                del self.runConfigDlg[old]
                del self.runConfig[old]

    def remove(self):
        row = self.listWidget.currentRow()
        item = self.listWidget.item(row)

        if str(item.text()) == 'Default':
            return

        if item is None:
            return
        reply = QMessageBox.question(self, "Remove {}".format(
                self.name), "Remove {} `{}'?".format(
                self.name, item.text()),
                QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            item = self.listWidget.takeItem(row)
            del item


    def run(self):        
        s = self.listWidget.currentItem().text()
        s = str(s)

        arg = self.runConfigDlg[s].get()

        parentDir = os.path.split(self.path)[0]        
        subprocess.Popen(arg, cwd = parentDir)
        self.runButton.setEnabled(False)
    
    def saveAs(self):
        row = self.listWidget.currentRow()
        if row < self.listWidget.count() - 1:
            item = self.listWidget.takeItem(row)
            self.listWidget.insertItem(row + 1, item)
            self.listWidget.setCurrentItem(item)

    def save(self):
        for x in self.runConfigDlg:
            self.runConfig[x] = self.runConfigDlg[x].get(Args = 'form')

        with closing(shelve.open(self.cfgPath, writeback = True)) as f:            
                f['runConfig'] = self.runConfig
  

    def revert(self):
        row = self.listWidget.currentRow()
        if row < self.listWidget.count() - 1:
            item = self.listWidget.takeItem(row)
            self.listWidget.insertItem(row + 1, item)
            self.listWidget.setCurrentItem(item)


    def reject(self):
        self.accept()


    def accept(self):
        QDialog.accept(self)

class RefitDlg(QWidget):

    def __init__(self, name, format, parent=None):
        super(RefitDlg, self).__init__(parent)        
        
        self.path = parent.path

        stepLabel = QLabel("&step -st ")
        self.stepEdit = QLineEdit(format["step"])
        stepLabel.setBuddy(self.stepEdit)

        tagLabel = QLabel("-tag")
        self.tagEdit = QLineEdit(format["tag"])
        tagLabel.setBuddy(self.tagEdit)

        numCoresLabel = QLabel("&numCores -nc")
        self.numCoresSpinBox = QSpinBox()
        numCoresLabel.setBuddy(self.numCoresSpinBox)
        self.numCoresSpinBox.setRange(1, 400)
        self.numCoresSpinBox.setValue(format["numCores"])
        
        self.writeDatesCheckBox = QCheckBox("&writeDates -w")
        self.writeDatesCheckBox.setChecked(format["writeDates"])

        self.clusterCheckBox = QCheckBox("&cluster -c")
        self.clusterCheckBox.setChecked(format["cluster"])

        self.ignoreCacheCheckCheckBox = QCheckBox("&ignoreCacheCheck -icc")
        self.ignoreCacheCheckCheckBox.setChecked(format["ignoreCacheCheck"])        

        self.format = format.copy()

        grid = QGridLayout()
        grid.addWidget(stepLabel, 0, 1)
        grid.addWidget(self.stepEdit, 0, 0)
        grid.addWidget(tagLabel, 1, 1)
        grid.addWidget(self.tagEdit, 1, 0)
        grid.addWidget(numCoresLabel, 2, 1)
        grid.addWidget(self.numCoresSpinBox, 2, 0)
        grid.addWidget(self.clusterCheckBox, 3, 0, 1, 2)
        grid.addWidget(self.ignoreCacheCheckCheckBox, 4, 0, 1, 2)
        grid.addWidget(self.writeDatesCheckBox, 5, 0, 1, 2)        
        self.setLayout(grid)
        
    def get(self, Args = 'run'):
        class ThousandsError(Exception): pass
        class DecimalError(Exception): pass
        Punctuation = frozenset(" ,;:.")

        step = self.stepEdit.text()
        tag = self.tagEdit.text()
        try:
            if len(tag) == 0:
                raise DecimalError("The decimal marker may not be "
                                   "empty.")
            if len(step) > 10000:
                raise ThousandsError("The thousands separator may "
                                     "only be empty or one character.")
            if len(tag) > 1000:
                raise DecimalError("The decimal marker must be "
                                   "one character.")
            if step == tag:
                raise ThousandsError("The thousands separator and "
                              "the decimal marker must be different.")
            if step and step not in Punctuation:
                raise ThousandsError("The thousands separator must "
                                     "be a punctuation symbol.")
            if tag not in Punctuation:
                raise DecimalError("The decimal marker must be a "
                                   "punctuation symbol.")
        except ThousandsError as e:
            QMessageBox.warning(self, "Thousands Separator Error", e)
            self.stepEdit.selectAll()
            self.stepEdit.setFocus()
            return
        except DecimalError as e:
            pass
            #QMessageBox.warning(self, "Decimal Marker Error", e)
            #self.tagEdit.selectAll()
            #self.tagEdit.setFocus()
            #return        
        
        # numCores  
        # writeDates
        # cluster
        # ignoreCacheCheck
        # tag
        # step

        self.format["step"] = str(step)
        self.format["tag"] =  str(tag)

        self.format["ignoreCacheCheck"] = (
                self.ignoreCacheCheckCheckBox.isChecked())

        self.format["cluster"] = (
                self.clusterCheckBox.isChecked())

        self.format["writeDates"] = (
                self.writeDatesCheckBox.isChecked())

        self.format["numCores"] = (
            self.numCoresSpinBox.value())        
        if Args == 'form':
            return self.format
        elif Args == 'run':
            arg=[]

            refitExe  = os.path.join(self.path, 'Refit.exe')
            parentDir = os.path.split(self.path)[0]

            arg.append(refitExe)

            if self.format["step"]:
                arg.append('-st')
                arg.append(self.format["step"])

            if self.format["tag"]:
                arg.append('-tag')
                arg.append(self.format["tag"])

            if self.format["writeDates"]:
                arg.append('-w')

            if self.format["cluster"]:
                arg.append('-c')

            if self.format["numCores"]:
               arg.append('-nc')
               arg.append(str(self.format["numCores"]))
        
            if self.format["ignoreCacheCheck"]:
                arg.append('-icc') 
        
        return arg
        
    def numberFormat(self):
        return self.format
