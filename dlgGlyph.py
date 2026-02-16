from PySide import QtCore, QtGui

import os
__dir__ = os.path.dirname(__file__)
inijs = os.path.join( __dir__, 'dlgGlyph.json')

from etFuncLayout import getIni, getKeys, getValue, writeIni, setValue

# https://jrgraphix.net/r/Unicode/0020-007F
# Constant definitions
userCancelled       = "Cancelled"
userOK              = "OK"

class dlgGlyph(QtGui.QDialog):
    
    def __init__(self, Family, *args):
        QtGui.QDialog.__init__(self, *args)
        self.ini = getIni(inijs)
        self.startFamily = Family
        self.setMinimumWidth(800)
        self.hbox = QtGui.QHBoxLayout()
        self.grid = None
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addLayout(self.__UI_Main__())
        self.layout().addLayout(self.__UI_Buttons__())        
        
    def __UI_Main__(self):
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.__UI_Font__())
        vbox.addLayout(self.__UI_Grid__())
        return vbox
        
    def __UI_Font__(self):
        debug = False
        if debug: print("Easytext dlgGlyph __UI_Font__ Start")
        hbox = QtGui.QHBoxLayout()
        self.cbFamily = QtGui.QFontComboBox()
        self.cbFamily.setObjectName("Format_" + "Family")
        self.cbFamily.activated.connect(self.onFontChanged)
        if self.startFamily:
            self.cbFamily.setCurrentFont(self.startFamily)
        hbox.addWidget(self.cbFamily)
        groupFamily = QtGui.QGroupBox("FontFamily:")
        groupFamily.setLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        self.sbPointSize = QtGui.QSpinBox()
        self.sbPointSize.setObjectName("Format_" + "PointSize")
        self.sbPointSize.setValue(8)
        self.sbPointSize.valueChanged.connect(self.onPointSizeChanged)
        hbox.addWidget(self.sbPointSize)
        groupPointSize = QtGui.QGroupBox("PointSize:")
        groupPointSize.setLayout(hbox)        
        
        hbox = QtGui.QHBoxLayout()
        self.cb = QtGui.QComboBox()
        self.cb.setEditable(False)
        self.cb.currentIndexChanged[int].connect(self.onUnicodeBlockChanged)
        options = getKeys(self.ini["UnicodeBlocks"])
        self.cb.addItems(getKeys(self.ini["UnicodeBlocks"]))
        #self.cb.setCurrentText("Low Surrogates")
        #print("LastBlock: " + str(self.ini["LastBlock"]))
        self.cb.setCurrentText(self.ini["LastBlock"])
        #print("self.cb.currentText(): " + str(self.cb.currentText()))
        hbox.addWidget(self.cb)
        groupBlock = QtGui.QGroupBox("Block:")
        groupBlock.setLayout(hbox)        
        
        hbox = QtGui.QHBoxLayout()        
        hbox.addWidget(groupFamily)
        hbox.addWidget(groupPointSize)
        hbox.addWidget(groupBlock)
        hbox.addWidget(QtGui.QLabel("Selected Text:"))
        self.label = QtGui.QLabel()
        hbox.addWidget(self.label)
        hbox.addStretch()
        if debug: print("Easytext dlgGlyph __UI_Font__ Ende")
        return hbox 

    def onUnicodeBlockChanged(self):
        debug = False
        if debug: print("Easytext dlgGlyph onUnicodeBlockChanged Start")        
        try:
            self.setFontTable()
            self.ini["LastBlock"] = self.sender().currentText()
        except:
            pass
        if debug: print("Easytext dlgGlyph onUnicodeBlockChanged Ende")
        
    def onFontChanged(self):
        debug = False
        if debug: print("Easytext dlgGlyph onFontChanged Start")
        self.setFontTable()
        if debug: print("Easytext dlgGlyph onFontChanged Ende")
        
    def onPointSizeChanged(self):
        debug = False
        if debug: print("Easytext dlgGlyph onPointSizeChanged Start")
        self.setFontTable()
        if debug: print("Easytext dlgGlyph onPointSizeChanged Ende")
        
    def __UI_Grid__(self):
        debug = False
        if debug: print("Easytext dlgGlyph __UI_Grid__ Start")
        self.grid = QtGui.QGridLayout()
        self.setFontTable()
        vBox = QtGui.QVBoxLayout()
        vBox.addLayout(self.hbox)
        #vBox.addWidget(self.placeholder)
        ui = QtGui.QWidget()        
        ui.setLayout(self.grid)
        scrollArea = QtGui.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(ui)
        vBox.addWidget(scrollArea) 
        if debug: print("Easytext dlgGlyph __UI_Grid__ Ende")
        return vBox
        
    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
        
    def setFontTable(self):     
        debug = False
        if debug: print("Easytext dlgGlyph setFontTable Start")
        maxBtns = 256
        self.clearLayout(self.hbox)
        if debug: print("self.cb.currentText(): " + str(self.cb.currentText()))
        strStart, strEnde = self.ini["UnicodeBlocks"][self.cb.currentText()]
        #self.cb = QtGui.QComboBox()
        #self.cb.setEditable(False)
        #options = getKeys(self.ini["UnicodeBlocks"])
        #self.cb.addItems(getKeys(self.ini["UnicodeBlocks"]))
        start = int(strStart, 16)
        ende = int(strEnde, 16)
        if (ende - start) > maxBtns:
            cbnext = self.comboNext(start, ende)
            self.hbox.addWidget(cbnext)
            self.btnsFontTable(start, start + 255)
        else:
            self.btnsFontTable(start, ende)
        if debug: print("Easytext dlgGlyph setFontTable Ende")
    
    def comboNext(self, start, ende):
        debug = False
        if debug: print("Easytext dlgGlyph comboNext Start")
        number = ende - start
        step = 255
        options = []
        page = 0
        for i1 in range(start, ende, step):
            page += 1
            if start + step < ende:
                option = "Page" + str(page)  + " : " + str(hex(i1)) + "-" + str(hex(i1+step))
            else:
                option = "Page" + str(page)  + " : " + str(hex(i1)) + "-" + str(hex(ende))
            print("option: " + str(option))
            options.append(option)
        self.cbnext = QtGui.QComboBox()
        self.cbnext.setEditable(False)
        self.cbnext.addItems(options)        
        self.cbnext.currentIndexChanged[int].connect(self.onPageChanged)
        if self.ini["LastPage"] in options:
            self.cbnext.setCurrentText(self.ini["LastPage"])
            if debug: print("LastPage: " + str(self.ini["LastPage"]))
        if debug: print("Easytext dlgGlyph comboNext Ende")
        return self.cbnext
        
    def onPageChanged(self):
        debug = False
        if debug: print("Easytext dlgGlyph onPageChanged Start")        
        if not self.grid:
            return
        text = self.sender().currentText()
        self.ini["LastPage"] = text
        if debug: print("text: " + str(text))
        if debug: print("self.grid: " + str(self.grid))
        start, ende = text.split(":")[-1].split("-")
        self.btnsFontTable(int(start, 16), int(ende, 16))
        if debug: print("start: " + str(start))
        if debug: print("Easytext dlgGlyph onPageChanged Ende")
        
    def btnsFontTable(self, start, ende):
        debug = False
        if debug: print("dlgGlyph btnsFontTable Start")
        try:
            btns = [widget for widget in self.grid.findChildren(QtGui.QPushButton)]
            [btn.deleteLater() for btn in btns]
        except:
            pass
        col = 0
        row = 0
        for i1 in range(start, ende + 0x1):
            if debug: print("i1: " + str(i1))
            if col > 7:
                col = 0
                row += 1
            char = chr(i1)
            #print("char: " + str(char))
            btn = QtGui.QPushButton(char)
            font = self.cbFamily.currentFont()
            font.setPointSize(self.sbPointSize.value())
            btn.setFont(font)
            btn.setToolTip(str(hex(i1)))
            btn.clicked.connect(self.onClick)
            self.grid.addWidget(btn, row, col)
            col += 1
        if debug: print("dlgGlyph btnsFontTable Ende")
        
    def onClick(self):
        debug = False
        if debug: print("Easytext dlgGlyph onClick Start")
        btn = self.sender()
        char = btn.text()
        font = btn.font()
        if debug: print("char: " + str(char))
        text = self.label.text()
        text += char
        self.label.setText(text)
        self.label.setFont(font)
        if debug: print("Easytext dlgGlyph onClick Ende")
        
        
    def __UI_Buttons__(self):
        hbox = QtGui.QHBoxLayout()
        # cancel button
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
        self.result         = userCancelled
        self.close()
        
    def onOk(self):
        self.result         = userOK
        self.close()
        
    def closeEvent(self, ev):        
        debug = False
        if debug: print("Easytext dlgGlyph closeEvent Start")
        writeIni(self.ini, inijs)

        if debug: print("Easytext dlgGlyph closeEvent Ende")



