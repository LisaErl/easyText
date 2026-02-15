from PySide import QtCore, QtGui

from urllib.request import urlretrieve
import os
__dir__ = os.path.dirname(__file__)

# Constant definitions
userCancelled       = "Cancelled"
userOK              = "OK"

from etFuncLayout import getIni, getKeys, getValue, writeIni, setValue
from etFunctions import _err, _info, _wrn

class dlgSettings(QtGui.QDialog):
    def __init__(self, ini):
        print("dlgSettings __init__ Start")
        QtGui.QDialog.__init__(self)
        self.ini = ini
        self.uinijs = os.path.join( __dir__, 'dlgGlyph.json')
        self.uini = getIni(self.uinijs)
        self.setWindowTitle("easyText Settings")
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().addLayout(self.__UI_Settings__())
        self.layout().addLayout(self.__UI_UnicodeBlocks__())
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

    def __UI_UnicodeBlocks__(self):
        hbox = QtGui.QHBoxLayout()
        lb = QtGui.QLabel("Unicode-Version: ")
        hbox.addWidget(lb)
        self.unicodeVersion = QtGui.QLineEdit()
        self.unicodeVersion.setText(self.uini["LastUnicodeVersion"])
        hbox.addWidget(self.unicodeVersion)
        unicodeButton = QtGui.QPushButton('Refresh')
        unicodeButton.clicked.connect(self.onRefreshUnicode)
        unicodeButton.setAutoDefault(False)
        hbox.addWidget(unicodeButton)
        return hbox

    def onRefreshUnicode(self):
        debug = False
        if debug: print("dlgSettings onRefreshUnicode Start")
        unicodeVersion = self.unicodeVersion.text()
        url = ("https://www.unicode.org/Public/" + unicodeVersion + "/ucd/Blocks.txt")
        file = os.path.join(__dir__, 'UnicodeBlocks.txt')
        try:
            urlretrieve(url, file)
        except:
            _err("onRefreshUnicode: The requested URL " + chr(34) + url + chr(34) + " was not found on the server.")
            return
        f = open(file,'r')
        txt = f.read()
        f.close()
        txt = txt[txt.index("\n0")+2:]
        lines = txt.split("\n")
        udict = {}
        for line in lines:
            if not line.startswith("#") and not line.startswith(" ") and not line == "":
                try:
                    blockcode, title = line.split(";")
                    title = title + "  (" + blockcode.replace("..", " -> ") + ")"
                    sStart, sEnde = blockcode.split("..")
                    udict[title] = [sStart, sEnde]
                except:
                    if debug: print("line: " + chr(34) + str(line) + chr(34))
        numblocks = len(udict.keys())
        _wrn("onRefreshUnicode: " + str(numblocks)  + " Unicode blocks have been updated.")
        if debug: print("unicodeVersion: " + str(unicodeVersion))
        self.uini["UnicodeBlocks"] = udict
        writeIni(self.uini, self.uinijs)
        if debug: print("dlgSettings onRefreshUnicode Ende")
        
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

