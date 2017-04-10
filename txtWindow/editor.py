from PyQt5 import QtGui, QtCore, QtWidgets
import os
              
class GenericEditor(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        QtWidgets.QTextEdit.__init__(self, parent)
        
        self.tab = '    '

        self.completer = None
        self.fileInfo = parent.fileInfo
        
        self.p = parent.p

        self.parent = parent

        self.name = self.fileInfo.fileName()
        self.path = self.fileInfo.absoluteFilePath()
        
        with open(self.path, "rt") as f: 
            self.setText(f.read())

        self.textChanged.connect(self.setDirty)

        #IndicatorHighlighter(self, "Classic" )
        self.setTabStopWidth(33)
        font = QtGui.QFont("Consolas", pointSize=13, weight=50, italic=False)
        self.setFont(font)
        #self.moveCursor(QtGui.QTextCursor.End)

        completer = self.getCompleter()
        self.setCompleter(completer)        

        # We need our own context menu for tables

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context)

        # If the cursor position changes, call the function that displays
        # the line and column number
        self.cursorPositionChanged.connect(self.cursorPosition)
           # We need our own context menu for tables

    def getCompleter(self):
        return None
        if not ('completer' in self.info):
            return
        if self.info['completer'] == 'ME_ENVIRONMENT':
            return MEEnvironmentCompleter(self.cfgPath, parent = None)
        elif self.info['completer'] == 'spec_parm':
            return MEEnvironmentCompleter(self.cfgPath, parent=None)
        elif self.info['completer'] == 'trade_ctrl':
            path = os.path.join(self.cfgPath, 'ctrl.lst')
            if os.path.exists(path):
                return TradeCtrlCompleter(path=path, parent=None)
        elif self.info['completer'] == 'swap_ctrl':
            path = os.path.join(self.cfgPath, 'swap_ctrl.lst')
            if os.path.exists(path):
                return TradeCtrlCompleter(path=path, parent=None)
        elif self.info['completer'] == 'exec_ctrl':
            path = os.path.join(self.cfgPath, 'exec_ctrl.lst')
            if os.path.exists(path):
                return TradeCtrlCompleter(path=path, parent=None)


    def setDirty(self):        
        if self.fileInfo.tmpView:
            self.parent.tmpView = None
        self.parent.setDirty(True)    

    def setCompleter(self, completer):
        if self.completer:
            self.disconnect(self.completer, 0, self, 0)
        if not completer:
            return
                    
        completer.setWidget(self)
        completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.completer = completer

        self.completer.activated[str].connect(self.insertCompletion)

    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = (completion.length() -
            self.completer.completionPrefix().length())
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion.right(extra))
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self);
        QtWidgets.QTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        if self.completer is None:
            QtWidgets.QTextEdit.keyPressEvent(self, event)
            return
           
        if event.key() == QtCore.Qt.Key_Tab:
            self.textCursor().insertText (QtCore.QString(self.tab))
            return 
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (
            QtCore.Qt.Key_Enter,
            QtCore.Qt.Key_Return,
            QtCore.Qt.Key_Escape,
            QtCore.Qt.Key_Tab,
            QtCore.Qt.Key_Backtab):
                event.ignore()
                return
        # has ctrl-E been pressed??
        isShortcut = (event.modifiers() == QtCore.Qt.ControlModifier and
                      event.key() == QtCore.Qt.Key_E)
        if (not self.completer or not isShortcut):
            QtWidgets.QTextEdit.keyPressEvent(self, event)
        # ctrl or shift key on it's own??
        ctrlOrShift = event.modifiers() in (QtCore.Qt.ControlModifier ,
                QtCore.Qt.ShiftModifier)
        if ctrlOrShift and event.text().isEmpty():
            # ctrl or shift key on it's own
            return
        eow = QtCore.QString("~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=") #end of word

        hasModifier = ((event.modifiers() != QtCore.Qt.NoModifier) and
                        not ctrlOrShift)
        completionPrefix = self.textUnderCursor()
        if (not isShortcut and (hasModifier or event.text().isEmpty() or
        completionPrefix.length() < 2 or
        eow.contains(event.text().right(1)))):
            self.completer.popup().hide()
            return
        if (completionPrefix != self.completer.completionPrefix()):
            self.completer.setCompletionPrefix(completionPrefix)
            popup = self.completer.popup()
            popup.setCurrentIndex(
                self.completer.completionModel().index(0,0))
        cr = self.cursorRect()        
        cr.setWidth(self.completer.popup().sizeHintForColumn(0)
        + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr) # popup it up!
    

    def closeView(self):
        return self.parent.close()

    def context(self,pos):
        # Grab the cursor
        cursor = self.textCursor()
        event = QtGui.QContextMenuEvent(QtGui.QContextMenuEvent.Mouse,QtCore.QPoint())
        self.contextMenuEvent(event)
            
    def save_as(self):
        # TODO:  make sure that parrent knows this operation
        
        tmp = self.path
        name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File As')
        if name : self.name = name
        with open(self.name,"w") as f:         
            f.write(self.toPlainText())
            f.close()

        self.parent.setDirty(False)

        del self.parent.openSet[self.path]

        self.parent.openSet[self.path] = str(name)
        self.parent.openSet[str(name)] = self.parent.openSet[self.path]

        del self.parent.openSet[self.path]

        self.path = str(name)

        if self == parent.tmpActive:
            self.parent.tmpActive = None
        
    def save(self):
        # Only open dialog if there is no filename yet        
        with open(self.name, "w") as f:
            f.write(self.toPlainText())                            
        self.parent.setDirty(False)        

    def preview(self):
        # Open preview dialog
        preview = QtWidgets.QPrintPreviewDialog()

        # If a print is requested, open print dialog
        preview.paintRequested.connect(lambda p: self.print_(p))

        preview.exec_()

    def printHandler(self):
        # Open printing dialog
        dialog = QtWidgets.QPrintDialog()

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.document().print_(dialog.printer())
    
    def cursorPosition(self):                

        cursor = self.textCursor()

        # Mortals like 1-indexed things
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber()
        
        self.parent.statusBar().showMessage("Line: {} | Column: {}".format(line,col))
        
    def indent(self):
        # Grab the cursor
        cursor = self.textCursor()
        if cursor.hasSelection():
            # Store the current line/block number
            temp = cursor.blockNumber()
            # Move to the selection's end
            cursor.setPosition(cursor.anchor())
            # Calculate range of selection
            diff = cursor.blockNumber() - temp
            direction = QtGui.QTextCursor.Up if diff > 0 else QtGui.QTextCursor.Down
            # Iterate over lines (diff absolute value)
            for n in range(abs(diff) + 1):
                # Move to start of each line
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                # Insert tabbing
                cursor.insertText("\t")
                # And move back up
                cursor.movePosition(direction)
        # If there is no selection, just insert a tab
        else:
            cursor.insertText("\t")

    def handleDedent(self, cursor):
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        # Grab the current line
        line = cursor.block().text()
        # If the line starts with a tab character, delete it
        if line.startsWith("\t"):
            # Delete next character
            cursor.deleteChar()
        # Otherwise, delete all spaces until a non-space character is met
        else:
            for char in line[:8]:
                if char != " ":
                    break
                cursor.deleteChar()

    def dedent(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            # Store the current line/block number
            temp = cursor.blockNumber()
            # Move to the selection's last line
            cursor.setPosition(cursor.anchor())
            # Calculate range of selection
            diff = cursor.blockNumber() - temp
            direction = QtGui.QTextCursor.Up if diff > 0 else QtGui.QTextCursor.Down
            # Iterate over lines
            for n in range(abs(diff) + 1):
                self.handleDedent(cursor)
                # Move up
                cursor.movePosition(direction)
        else:
            self.handleDedent(cursor)

    def on_text_changed(self):
        pass


 
class TradeCtrlCompleter(QtWidgets.QCompleter):
    def __init__(self, path='', parent=None):
        import trade_ctrl
        words = []
        for x in open(path):
            words.append(x)
            QtWidgets.QCompleter.__init__(self, words, parent)

class IndicatorHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent, theme ):
      QtGui.QSyntaxHighlighter.__init__(self, parent )
      self.parent = parent
      keyword = QtGui.QTextCharFormat()
      reservedClasses = QtGui.QTextCharFormat()
      assignmentOperator = QtGui.QTextCharFormat()
      delimiter = QtGui.QTextCharFormat()
      specialConstant = QtGui.QTextCharFormat()
      boolean = QtGui.QTextCharFormat()
      number = QtGui.QTextCharFormat()
      comment = QtGui.QTextCharFormat()
      string = QtGui.QTextCharFormat()
      singleQuotedString = QtGui.QTextCharFormat()

      self.highlightingRules = []

      # keyword
      brush = QtGui.QBrush(QtGui.QColor(111, 0, 138), QtCore.Qt.SolidPattern ) # "#4169E1"
      keyword.setForeground( brush )
      #keyword.setFontWeight( QFont.Bold )
      keywords = QtCore.QStringList([
            "numpy",
           ])
      for word in keywords:
        pattern = QtCore.QRegExp("\\b" +"d*"+word + "[DHA]*\\b")
        rule = HighlightingRule( word, keyword )
        self.highlightingRules.append( rule )

      # reservedClasses
      brush = QtGui.QBrush(QtGui.QColor(0, 0, 255 ), QtCore.Qt.SolidPattern )# 9400D3
      reservedClasses.setForeground( brush )
      #reservedClasses.setFontWeight( QFont.Bold )
      keywords =    QtCore.QStringList([ 
        "Histogram",
        "Decorr",
        "CLIP"])
      for word in keywords:
        pattern = QtCore.QRegExp("\\b" + word + "\\b")
        rule = HighlightingRule( pattern, reservedClasses )
        self.highlightingRules.append( rule )
      # assignmentOperator
      brush = QtGui.QBrush( QtGui.QColor(180, 180, 180), QtCore.Qt.SolidPattern )
      pattern = QtCore.QRegExp( "(<){1,2}-" )
      assignmentOperator.setForeground( brush )
      #assignmentOperator.setFontWeight( QFont.Bold )
      rule = HighlightingRule( pattern, assignmentOperator )
      self.highlightingRules.append(rule)      
      # delimiter
      pattern = QtCore.QRegExp( "[\)\(]+|[\{\}]+|[][]+" )
      delimiter.setForeground( brush )
      delimiter.setFontWeight(QtGui.QFont.Bold )
      rule = HighlightingRule( pattern, delimiter )
      self.highlightingRules.append( rule )
      # specialConstant
      brush = QtGui.QBrush(QtGui.QColor(43, 145, 175), QtCore.Qt.SolidPattern )
      specialConstant.setForeground( brush )
      keywords = QtCore.QStringList([ "Inf", "NA", "NaN", "NULL", "REJECT", "SKIPZERO"])
      for word in keywords:
        pattern = QtCore.QRegExp("\\b" + word + "\\b")
        rule = HighlightingRule( pattern, specialConstant )
        self.highlightingRules.append( rule )
      # boolean
      QtGui.brush = QtGui.QBrush(QtGui.QColor(255, 0, 0), QtCore.Qt.SolidPattern )
      boolean.setForeground(brush)
      keywords =  QtCore.QStringList([ "TRUE", "FALSE" ])
      for word in keywords:
        pattern = QtCore.QRegExp("\\b" + word + "\\b")
        rule = HighlightingRule( pattern, boolean )
        self.highlightingRules.append( rule )
      # number
      brush = QtGui.QBrush(QtGui.QColor(181, 206, 168), QtCore.Qt.SolidPattern )
      pattern = QtCore.QRegExp( "[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?" )
      pattern.setMinimal( True )
      number.setForeground( brush )
      rule = HighlightingRule( pattern, number )
      self.highlightingRules.append(rule)
      # comment
      brush = QtGui.QBrush(QtGui.QColor(87,166, 74), QtCore.Qt.SolidPattern )
      pattern = QtCore.QRegExp( "^\s*#[^\n]*" )
      comment.setForeground( brush )
      #comment.setFontWeight( QFont.Bold )
      rule = HighlightingRule( pattern, comment )
      self.highlightingRules.append(rule)
      # string
      brush = QtGui.QBrush(QtGui.QColor(214, 157, 133), QtCore.Qt.SolidPattern )
      pattern = QtCore.QRegExp( "\".*\"" )
      pattern.setMinimal( True )
      string.setForeground( brush )
      rule = HighlightingRule( pattern, string )
      self.highlightingRules.append(rule)      
      # singleQuotedString
      pattern = QtCore.QRegExp( "\'.*\'" )
      pattern.setMinimal( True )
      singleQuotedString.setForeground( brush )
      rule = HighlightingRule( pattern, singleQuotedString )
      self.highlightingRules.append(rule)

    def highlightBlock( self, text ):
      for rule in self.highlightingRules:
        expression = QtCore.QRegExp( rule.pattern )
        index = expression.indexIn( text )
        while index >= 0:
          length = expression.matchedLength()
          self.setFormat( index, length, rule.format )
          index = text.indexOf( expression, index + length )
      self.setCurrentBlockState( 0 )

class HighlightingRule():
  def __init__( self, pattern, format ):
    self.pattern = pattern
    self.format = format