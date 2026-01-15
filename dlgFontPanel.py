from PySide import QtCore, QtGui

import pathlib
import os
__dir__ = os.path.dirname(__file__)
iconDir = os.path.join( __dir__, "Icons")

# Stylesheet with expand/collapse icon instead of the checkbox of a QGroupBox.
pathtrue = pathlib.PurePath(os.path.join(iconDir, "ExpInact.svg"))
pathfalse = pathlib.PurePath(os.path.join(iconDir, "ExpAct.svg"))
stylesize = "QGroupBox::indicator {width:13px;height: 13px;}"
stylechecked = "QGroupBox::indicator:checked {image: url(" + pathfalse.as_posix() + ");}"
styleunchecked = "QGroupBox::indicator:unchecked {image: url(" + pathtrue.as_posix() + ");}"
expandStyle4GroupBox = ''.join([stylesize, stylechecked, styleunchecked])

class fontFormatWidget(QtGui.QWidget):
    
    fontChanged = QtCore.Signal(object)
    resized = QtCore.Signal()
    
    def __init__(self, qfont, pointsize, buttonsize, lBox, texttype, *args):
        debug = True
        if debug:  print("fontFormatWidget __init__ Start")
        QtGui.QWidget.__init__(self, *args)
        if debug: print("texttype: " + str(texttype))
        self.qfont = qfont
        self.pointsize = pointsize
        self.buttonsize = buttonsize
        self.lBox = lBox
        self.setLayout(QtGui.QVBoxLayout())
        self.texttype = texttype
        self.layout().addLayout(self.__UI_Format_Panel__())
        self.layout().addStretch(1)
        if debug:  print("fontFormatWidget __init__ Ende")
        
    def __UI_Format_Panel__(self):
        self.fontLayout = QtGui.QVBoxLayout()        
        self.fontLayout.addLayout(self.__UI_Font__())
        self.fontLayout.addLayout(self.__UI_FormatsShort__())
        self.fontLayout.addLayout(self.__UI_FormatsExtended__())
        return self.fontLayout
        
    def __UI_Font__(self):
        hbox = QtGui.QHBoxLayout()
        self.cbFamily = QtGui.QFontComboBox()
        self.cbFamily.setCurrentFont(self.qfont)
        self.cbFamily.currentFontChanged.connect(self.onFontComboChanged)
        self.cbFamily.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        hbox.addWidget(self.cbFamily)
        family = self.qfont.family()
        styles = QtGui.QFontDatabase().styles(family)
        try:
            formatfont = QtGui.QFontDatabase().font(family, styles[0], 20)
            self.cbFamily.setFont(formatfont)
        except:
            formatfont = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.GeneralFont)
        
        groupFamily = QtGui.QGroupBox("FontFamily:")
        groupFamily.setLayout(hbox)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(groupFamily)
        hbox.addStretch()
        return hbox         
        
    def onFontComboChanged(self):
        family = self.cbFamily.currentFont().family()
        self.qfont.setFamily(family)
        self.fontChanged.emit(self.qfont)
        self.cbFamily.setFont(QtGui.QFontDatabase().font(family, QtGui.QFontDatabase().styles(family)[0], 16))        
        
    def __UI_FormatsShort__(self):
        debug = True
        if debug: print("fontFormatWidget __UI_FormatsShort__ Start")
        if self.texttype == "easyTextGlyphs":
            formats = ["bold", "italic"]
        else:
            formats = ["bold", "italic", "underline", "strikeOut", "overline"]
        iconpath = os.path.join(__dir__, 'icons')
        size = QtCore.QSize(self.buttonsize, self.buttonsize)
        hbox = QtGui.QHBoxLayout()
        self.bGroup = QtGui.QButtonGroup()
        self.bGroup.setExclusive(False)
        for key in formats:
            name = key
            iconpathOn = os.path.join(iconpath, "F_" + key + ".svg")
            iconpathOff = os.path.join(iconpath, "F_" + key + "Inact.svg")
            icon = QtGui.QIcon()
            icon.addFile(iconpathOn, size, mode=icon.Normal, state=icon.On)
            icon.addFile(iconpathOff, size, mode=icon.Normal, state=icon.Off)
            btn = QtGui.QToolButton()
            btn.setIconSize(size)
            btn.setCheckable(True)
            btn.setIcon(icon)
            btn.setChecked(self.qfont.__getattribute__(key)())
            btn.setObjectName("Format_" + key)
            btn.setToolTip(key)
            btn.clicked.connect(self.onGroupBtnChanged) 
            self.bGroup.addButton(btn)
            hbox.addWidget(btn)
        hbox.addStretch()
        groupBox = QtGui.QGroupBox("Short Format:")
        groupBox.setLayout(hbox)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(groupBox)
        vbox.addStretch()
        if debug: print("fontFormatWidget __UI_FormatsShort__ Ende")
        return vbox 
        
    def onGroupBtnChanged(self):
        debug = False
        if debug: print("fontFormatWidget onGroupBtnChanged Start")        
        ident = self.sender().objectName().split("_")
        key = ident[-1]        #
        if key == "bold": 
            if self.sender().isChecked():
                self.qfont.setWeight(QtGui.QFont.Weight.Bold)
            else:
                self.qfont.setWeight(QtGui.QFont.Weight.Normal)
        else:
            if key == "italic":
                self.qfont.setItalic(self.sender().isChecked())
            elif key == "underline":
                self.qfont.setUnderline(self.sender().isChecked())
            elif key == "overline":
                self.qfont.setOverline(self.sender().isChecked())
            elif key == "strikeOut":
                self.qfont.setStrikeOut(self.sender().isChecked())
        self.fontChanged.emit(self.qfont)
        if debug: print("fontFormatWidget onGroupBtnChanged Ende")

    def __UI_FormatsExtended__(self):
        debug = False
        if debug: print("fontFormatWidget __UI_FormatsExtended__ Start")
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.__UI_Spacing__())
        vbox.addLayout(self.__UI_WeightStyleCapitalize__())        
        group = QtGui.QGroupBox("Extended formatting:")
        group.setStyleSheet(expandStyle4GroupBox)
        group.setLayout(vbox)        
        group.setCheckable(True)
        group.setChecked(True)
        group.toggled.connect(self.onToggleGroup)
        if debug: print("self.sizeHint(): " + str(self.sizeHint()))
        if group.isChecked():
            group.setFixedHeight(group.sizeHint().height())
        else:
            group.setFixedHeight(30)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(group)
        if debug: print("fontFormatWidget __UI_FormatsExtended__ Ende")
        return vbox
        
    def onToggleGroup(self):
        debug = False
        if debug: print("fontFormatWidget onToggleGroup Start")        
        group = self.sender()
        if group.isChecked():
            group.setFixedHeight(group.sizeHint().height())
        else:
            group.setFixedHeight(30)
        self.resized.emit()
        if debug: print("fontFormatWidget onToggleGroup Ende")
        
    def __UI_Spacing__(self):
        print("dlgFormat __UI_Spacing__ Start")        
        hbox = QtGui.QHBoxLayout()
        sbl = QtGui.QSpinBox()
        sbl.setMinimum(-100)
        sbl.setMaximum(100)
        sbl.valueChanged.connect(self.onLetterSpacing)        
        sbl.setToolTip("Letter spacing changes the default spacing between individual letters in the font. The spacing between the letters can be made smaller as well as larger")
        sbl.setValue(self.qfont.letterSpacing())
        hbox.addWidget(sbl)
        hbox.addStretch()
        groupl = QtGui.QGroupBox("Letter Spacing:")
        groupl.setLayout(hbox)        
        
        hbox = QtGui.QHBoxLayout()
        sbw = QtGui.QSpinBox()
        sbw.setMinimum(-100)
        sbw.setMaximum(100)
        sbw.valueChanged.connect(self.onWordSpacing)        
        sbw.setToolTip("Word spacing changes the default spacing between individual words. A positive value increases the word spacing by a corresponding amount of pixels, while a negative value decreases the inter-word spacing accordingly.")
        sbw.setValue(self.qfont.wordSpacing())
        hbox.addWidget(sbw)
        hbox.addStretch()
        groupw = QtGui.QGroupBox("Word Spacing:")
        groupw.setLayout(hbox)                
        
        hbox = QtGui.QHBoxLayout()
        sbr = QtGui.QSpinBox()
        sbr.setMinimum(0)
        sbr.setMaximum(4000)
        sbr.valueChanged.connect(self.onStretch)        
        sbr.setToolTip("The stretch factor matches a condensed or expanded version of the font or applies a stretch transform that changes the width of all characters in the font by factor percent. For example, setting factor to 150 results in all characters in the font being 1.5 times (ie. 150%) wider. The minimum stretch factor is 1, and the maximum stretch factor is 4000. The default stretch factor is AnyStretch, which will accept any stretch factor and not apply any transform on the font.")
        if self.qfont.stretch() == 0: 
            self.qfont.setStretch(100)
            self.fontChanged.emit(self.qfont)
        sbr.setValue(self.qfont.stretch())
        hbox.addWidget(sbr)
        hbox.addStretch()
        groupr = QtGui.QGroupBox("Stretch:")
        groupr.setLayout(hbox)        

        if isinstance(self.lBox, QtGui.QHBoxLayout):
            #print("QHBoxLayout")
            lBox = QtGui.QHBoxLayout()
        elif isinstance(self.lBox, QtGui.QVBoxLayout):
            #print("QVBoxLayout")
            lBox = QtGui.QVBoxLayout()
        lBox.addWidget(groupl)
        lBox.addWidget(groupw)
        #lBox.addWidget(groupr) 
        lBox.addStretch()
        print("dlgFormat __UI_Spacing__ Ende")
        return lBox                 
        
    def onStretch(self):
        print("dlgFormat onStretch Start")
        value = self.sender().value()
        print("value: " + str(value))
        self.qfont.setStretch(value)
        self.fontChanged.emit(self.qfont)
        print("dlgFormat onStretch Ende")
        
    def onLetterSpacing(self):
        #print("dlgFormat onLetterSpacing Start")
        value = self.sender().value()
        #print("value: " + str(value))
        self.qfont.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, value)
        self.fontChanged.emit(self.qfont)
        #print("dlgFormat onLetterSpacing Ende")
        
    def onWordSpacing(self):
        #print("dlgFormat onWordSpacing Start")
        value = self.sender().value()
        #print("value: " + str(value))
        self.qfont.setWordSpacing(value)
        self.fontChanged.emit(self.qfont)
        #print("dlgFormat onWordSpacing Ende")
        
    def __UI_WeightStyleCapitalize__(self):
        #print("dlgFormat __UI_WeightStyleCapitalize__ Start")        
        #hbox = QtGui.QHBoxLayout()
        groupw = self.__UI_EnumGroup__(QtGui.QFont.Weight) 
        groups = self.__UI_EnumGroup__(QtGui.QFont.Style)   
        groupc = self.__UI_EnumGroup__(QtGui.QFont.Capitalization)        
        if isinstance(self.lBox, QtGui.QHBoxLayout):
            #print("QHBoxLayout")
            lBox = QtGui.QHBoxLayout()
        elif isinstance(self.lBox, QtGui.QVBoxLayout):
            #print("QVBoxLayout")
            lBox = QtGui.QVBoxLayout()
        lBox.addWidget(groupw) 
        lBox.addWidget(groups)
        lBox.addWidget(groupc)
        lBox.addStretch()
        #print("dlgFormat __UI_WeightStyleCapitalize__ Ende")
        return lBox         
        
    def getEnumKeyAsString(self, enum):
        return str(enum).split(".")[-1].replace("'>", "")
        
    def getAttrFromEnum(self, enum):
        strkey = str(enum).split(".")[-1].replace("'>", "")
        return strkey[0].lower() + strkey[1:]
        
    def getCurrentEnumValueAsString(self, enum):
        #print("dlgFormat getCurrentEnumValueAsString Start")
        attr = self.getAttrFromEnum(enum)
        val = self.qfont.__getattribute__(attr)()
        strval = str(val).split(".")[-1]
        #print("strval: " + str(strval))
        if strval.isdigit():
            strval = [key for key in list(enum.values.keys()) if int(strval) == int(enum.values[key])][0]
            #keys = [key for key in enumerate(list(enum.values.keys())) if int(enum.values[key]) == strval]
            #print("strval: " + str(strval))
        #print("dlgFormat getCurrentEnumValueAsString Ende")
        return strval
        
    def __UI_EnumGroup__(self, enum):
        #print("dlgFormat __UI_EnumGroup__ Start")
        #print("enum: " + str(enum))
        hbox = QtGui.QHBoxLayout()
        options = list(enum.values.keys())
        #print("options: " + str(options))
        title = self.getEnumKeyAsString(enum)
        #print("title: " + str(title))     
        cur = self.getCurrentEnumValueAsString(enum)
        #print("cur: " + str(cur))
        self.cbEnum = QtGui.QComboBox()
        self.cbEnum.setEditable(False)        
        self.cbEnum.addItems(options)
        self.cbEnum.setCurrentText(cur)
        self.cbEnum.currentIndexChanged[int].connect(self.cbEnumOptionChanged)
        self.cbEnum.setObjectName(title)
        hbox.addWidget(self.cbEnum)
        hbox.addStretch()
        group = QtGui.QGroupBox(title + ":")
        group.setLayout(hbox) 
        #print("dlgFormat __UI_EnumGroup__ Ende")
        return group
        
    def cbEnumOptionChanged(self, index):
        print("dlgFormat cbEnumOptionChanged Start")
        print("index: " + str(index))
        if self.sender().objectName() == "Weight" :
            enum = QtGui.QFont.Weight
        elif self.sender().objectName() == "Style" :
            enum = QtGui.QFont.Style
        elif self.sender().objectName() == "Capitalization" :
            enum = QtGui.QFont.Capitalization
        key = list(enum.values.keys())[index]
        value = enum.values[key]
        print("enum: " + str(enum))
        print("key: " + str(key))
        print("value: " + str(value))
        if self.sender().objectName() == "Weight" :
            self.qfont.setWeight(value)
        elif self.sender().objectName() == "Style" :
            self.qfont.setStyle(value)
        elif self.sender().objectName() == "Capitalization" :
            self.qfont.setCapitalization(value)
        self.fontChanged.emit(self.qfont)       
        print("dlgFormat cbEnumOptionChanged Ende")