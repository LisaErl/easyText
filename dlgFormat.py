from PySide import QtCore, QtGui

import os
__dir__ = os.path.dirname(__file__)
inijs = os.path.join( __dir__, 'dlgFormat.json')

# Constant definitions
userCancelled       = "Cancelled"
userOK              = "OK"

from etFuncLayout import getIni, writeIni
from dlgSettings import dlgSettings
from dlgGlyph import dlgGlyph
import dlgFontPanel

class dlgFormat(QtGui.QDialog):
    
    def __init__(self, qfont, text, texttype):
        debug = False
        if debug: print("dlgFormat __init__ Start")
        QtGui.QDialog.__init__(self)
        if debug: print("texttype: " + str(texttype))
        self.ini = getIni(inijs)
        self.qfont = qfont
        self.qfont.setPointSize(self.ini["Settings"]["Pointsize"]["Value"])
        self.setWindowTitle("easyText Format")
        self.setLayout(QtGui.QVBoxLayout())
        self.menuBar = self.__UI_Menubar__()
        self.layout().setMenuBar(self.menuBar)
        self.layout().addLayout(self.__UI_Text__(text))        
        #self.layout().addLayout(self.__UI_Format_Panel__())
        widget = dlgFontPanel.fontFormatWidget(qfont, self.ini["Settings"]["Pointsize"]["Value"], self.ini["Settings"]["Buttonsize"]["Value"], QtGui.QHBoxLayout(), texttype)
        widget.fontChanged.connect(self.onFontChanged)
        widget.resized.connect(self.onResized)
        self.layout().addWidget(widget)
        #self.layout().addStretch(1)
        #self.layout().addStretch(1)
        self.layout().addLayout(self.__UI_Buttons__())
        self.layout().addStretch(1)
        if debug: print("dlgFormat __init__ Ende")
        
    def onResized(self):
        debug = True
        if debug: print("dlgTest onResized Start")
        self.resize(0,0)
        self.adjustSize()
        print("self.sizeHint().height(): " + str(self.sizeHint().height()))
        print("self.height(): " + str(self.height()))
        if debug: print("dlgTest onResized Ende")
        
    def onFontChanged(self):
        debug = False
        if debug: print("dlgFormat onFontChanged Start")
        if debug: print("qfont: " + str(self.sender().qfont))
        if debug: print("qfont.stretch: " + str(self.sender().qfont.stretch()))
        self.qfont = self.sender().qfont
        self.lineedit.setFont(self.qfont)
        if debug: print("dlgFormat onFontChanged Ende")
        
    def __UI_Menubar__(self):
        #print("dlgFormat __UI_Menubar__ Start")        
        menu = QtGui.QMenuBar()
        setMenu = QtGui.QMenu("Settings", self)
        menu.addMenu(setMenu)
        setAction = QtGui.QAction("&Change ...", self)
        setAction.setStatusTip("Dialog to change the Settings")
        setAction.triggered.connect(self.callDialogSettings)
        setMenu.addAction(setAction)
        return menu
        
    def callDialogSettings(self):
        #print("dlgFormat callDialogSettings Start")    
        form = dlgSettings(self.ini)
        form.exec_()
        if form.result == "OK":
            #print("form.result: " + str(form.result))
            self.ini = form.ini
            writeIni(self.ini, inijs)
        #print("dlgFormat callDialogSettings Ende")
        
    def __UI_Text__(self, text):        
        hbox = QtGui.QHBoxLayout()
        self.lineedit = QtGui.QLineEdit()
        self.lineedit.setText(text)
        self.lineedit.setFont(self.qfont)
        self.lineedit.editingFinished.connect(self.onTextChanged)
        #self.lineedit.setStyleSheet("font-style: oblique 40")
        hbox.addWidget(self.lineedit)
        groupText = QtGui.QGroupBox("Text:")
        groupText.setLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        btn = QtGui.QPushButton('Glyph-Table')
        btn.setAutoDefault(False)
        btn.clicked.connect(self.onGlyphTable)
        hbox.addWidget(btn)
        groupGlyph = QtGui.QGroupBox("Insert Glyph:")
        groupGlyph.setLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        self.hexedit = QtGui.QLineEdit()
        self.hexedit.setInputMask("HHHH")
        self.hexedit.setText("00A9")
        hbox.addWidget(self.hexedit)
        btn = QtGui.QPushButton('Insert Char')
        btn.clicked.connect(self.onHexInsert)
        btn.setAutoDefault(False)
        hbox.addWidget(btn)
        groupHex = QtGui.QGroupBox("Insert Hex:")
        groupHex.setLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(groupText)
        hbox.addWidget(groupHex)
        hbox.addWidget(groupGlyph)
        return hbox        
        
    def onHexInsert(self):
        print("dlgFormat onGlyphTable Start")
        text = self.hexedit.text()
        print("text: " + str(text))
        x = int(text, 16)
        print("x: " + str(x))
        print("char: " + str(chr(int(x))))
        QtGui.QClipboard().setText(chr(int(x)))
        self.lineedit.paste()        
        
    def onGlyphTable(self):
        print("dlgFormat onGlyphTable Start")
        form = dlgGlyph(Family = self.qfont.family())
        form.exec_()
        print("form.result: " + str(form.result))
        if form.result == "OK":
            text = form.label.text()
            font = form.label.font()
            print("text: " + str(text))
            print("font: " + str(font))
            #cursor = self.textEdit.textCursor()
            #cursor.insertText(text)
            QtGui.QClipboard().setText(text)
            self.lineedit.paste()
        print("dlgFormat onGlyphTable Ende")
        
    def onTextChanged(self):
        print("dlgFormat onTextChanged Start")
        print("dlgFormat onTextChanged Ende")
        
    def __UI_Buttons__(self):
        hbox = QtGui.QHBoxLayout()
        # Cancel button
        cancelButton = QtGui.QPushButton('Cancel', self)
        cancelButton.clicked.connect(self.onCancel)
        cancelButton.setAutoDefault(False)
        # OK button
        okButton = QtGui.QPushButton('OK', self)
        okButton.clicked.connect(self.onOk)
        okButton.setAutoDefault(True)
        hbox.addWidget(cancelButton)
        hbox.addWidget(okButton)
        return hbox
        
    def onCancel(self):
        print("dlgFormat onCancel Start")
        #self.result = self.fontstr        
        self.result = userCancelled
        
        self.close()
        print("dlgFormat onCancel Ende")
        
    def getText(self):
        return self.lineedit.text()
        
    def onOk(self):
        print("dlgFormat onOk Start")
        #self.result = self.qfont.toString()
        self.result = userOK
        self.close()
        print("dlgFormat onOk Ende")