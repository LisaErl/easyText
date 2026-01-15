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
        print("Easytext __UI_Font__ Start")
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
        print("Easytext __UI_Font__ Ende")
        return hbox 

    def onUnicodeBlockChanged(self):
        print("Easytext onUnicodeBlockChanged Start")        
        try:
            self.setFontTable()
            self.ini["LastBlock"] = self.sender().currentText()
        except:
            pass
        print("Easytext onUnicodeBlockChanged Ende")
        
    def onFontChanged(self):
        print("Easytext onFontChanged Start")
        self.setFontTable()
        print("Easytext onFontChanged Ende")
        
    def onPointSizeChanged(self):
        print("Easytext onPointSizeChanged Start")
        self.setFontTable()
        print("Easytext onPointSizeChanged Ende")
        
    def __UI_Grid__(self):
        print("Easytext __UI_Grid__ Start")
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
        print("Easytext __UI_Grid__ Ende")
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
        print("Easytext setFontTable Start")
        maxBtns = 256
        self.clearLayout(self.hbox)
        print("self.cb.currentText(): " + str(self.cb.currentText()))
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
        print("Easytext setFontTable Ende")
    
    def comboNext(self, start, ende):
        print("Easytext comboNext Start")
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
            print("LastPage: " + str(self.ini["LastPage"]))
        print("Easytext comboNext Ende")
        return self.cbnext
        
    def onPageChanged(self):
        print("Easytext onPageChanged Start")        
        if not self.grid:
            return
        text = self.sender().currentText()
        self.ini["LastPage"] = text
        print("text: " + str(text))
        print("self.grid: " + str(self.grid))
        start, ende = text.split(":")[-1].split("-")
        self.btnsFontTable(int(start, 16), int(ende, 16))
        print("start: " + str(start))
        print("Easytext onPageChanged Ende")
        
    def btnsFontTable(self, start, ende):
        try:
            btns = [widget for widget in self.grid.findChildren(QtGui.QPushButton)]
            [btn.deleteLater() for btn in btns]
        except:
            pass
        col = 0
        row = 0
        for i1 in range(start, ende + 0x1):
            #print("i1: " + str(i1))
            if col > 7:
                col = 0
                row += 1
            char = chr(i1)
            #print("char: " + str(char))
            btn = QtGui.QPushButton(char)
            font = self.cbFamily.currentFont()
            font.setPointSize(self.sbPointSize.value())
            btn.setFont(font)
            btn.clicked.connect(self.onClick)
            self.grid.addWidget(btn, row, col)
            col += 1
        
    def onClick(self):
        btn = self.sender()
        char = btn.text()
        font = btn.font()
        print("char: " + str(char))
        text = self.label.text()
        text += char
        self.label.setText(text)
        self.label.setFont(font)
        
        
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
        print("Easytext closeEvent Start")
        writeIni(self.ini, inijs)
        print("Easytext closeEvent Ende")