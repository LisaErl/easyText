from PySide import QtCore, QtGui

import os
__dir__ = os.path.dirname(__file__)

# Constant definitions
userCancelled       = "Cancelled"
userOK              = "OK"

from etFuncLayout import getIni, getKeys, getValue, writeIni, setValue

class dlgSettings(QtGui.QDialog):
    def __init__(self, ini):
        print("dlgSettings __init__ Start")
        QtGui.QDialog.__init__(self)
        self.ini = ini
        self.setWindowTitle("easyText Settings")
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().addLayout(self.__UI_Settings__())
        self.layout().addLayout(self.__UI_Buttons__())
        print("dlgSettings __init__ Ende")
        
    def __UI_Settings__(self):
        keylist = ["Settings"]
        vbox = QtGui.QVBoxLayout()
        keys = getKeys(self.ini, keylist)
        for key in keys:
            vbox.addLayout(self.__UI_Setting__(keylist + [key]))
        vbox.addStretch()
        lb = QtGui.QLabel("Updates will take effect at next start of the dialog")
        lb.setStyleSheet("color: red;")
        vbox.addWidget(lb)
        return vbox        
        
    def __UI_Setting__(self, keylist):
        hbox = QtGui.QHBoxLayout()
        text = getValue(self.ini, "Text", keylist)
        value = getValue(self.ini, "Value", keylist)
        tooltip = getValue(self.ini, "Tooltip", keylist)
        lb = QtGui.QLabel(text + ": ")
        font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.GeneralFont)
        font.setPointSize(8)
        lb.setFont(font)
        hbox.addWidget(lb)
        if isinstance(value, int):
            sb = QtGui.QSpinBox()
            sb.setValue(value)
            sb.setObjectName('_'.join(keylist))
            sb.valueChanged.connect(self.onSettingChanged)
            sb.setToolTip(tooltip)
            hbox.addWidget(sb)
        return hbox        
        
    def onSettingChanged(self):
        keylist = self.sender().objectName().split("_") 
        print("keylist: " + str(keylist))
        value = self.sender().value()
        print("value: " + str(value))
        setValue(self.ini, value, "Value", keylist)
        
    def __UI_Buttons__(self):
        hbox = QtGui.QHBoxLayout()
        # Takes effect at next start
        # Cancel button
        cancelButton = QtGui.QPushButton('Cancel', self)
        cancelButton.clicked.connect(self.onCancel)
        cancelButton.setAutoDefault(False)
        # OK button
        okButton = QtGui.QPushButton('OK', self)
        okButton.clicked.connect(self.onOk)
        okButton.setAutoDefault(False)
        hbox.addWidget(cancelButton)
        hbox.addWidget(okButton)
        return hbox
        
    def onCancel(self):
        print("dlgFormat onCancel Start")
        #self.result = self.fontstr        
        self.result = userCancelled        
        self.close()
        print("dlgFormat onCancel Ende")
        
    def onOk(self):
        print("dlgFormat onOk Start")
        #self.result = self.qfont.toString()
        self.result = userOK
        self.close()
        print("dlgFormat onOk Ende")