# -*- coding: utf-8 -*-

__title__ = "easyText"
__author__ = "Lisa Erlingheuser"
__doc__ = "easyText"

from PySide import QtCore, QtGui
from PySide.QtCore import QT_TRANSLATE_NOOP
import FreeCAD, FreeCADGui

import os

import Part

import etFunctions as etf
import dlgFormat

__dir__ = os.path.dirname(__file__)

translate = QtCore.QCoreApplication.translate

def executeObject(obj):
    debug = False
    if debug:  print("easyTextGlyphs executeObject Start")
    if obj.TextShape == "Wires":
        shapes, obj.Font, obj.DescenderList = etf.makeWiresTextGlyphs(obj.Text, obj.Font, obj.FontExt, obj.Height, obj.Width)    
    elif obj.TextShape == "Faces":
        shapes, obj.Font, obj.DescenderList = etf.makeFacesTextGlyphs(obj.Text, obj.Font, obj.FontExt, obj.Height, obj.Width, obj.TextShapeFusion)
    elif obj.TextShape == "Extrusion":
        shapes, obj.Font, obj.DescenderList = etf.makeExtrudesTextGlyphs(obj.Text, obj.Font, obj.FontExt, obj.TextShapeExtrusion, obj.Height, obj.Width, obj.TextShapeFusion)
    if shapes:
        obj.Shape = Part.Compound(shapes)
    else:
        obj.Shape = Part.Shape()
        obj.ViewObject.hide()
    if debug:  print("easyTextGlyphs executeObject Ende")

def initPropertiesObject(obj):
    debug = False
    if debug: print("easyTextGlyphs initPropertiesObject Start")
    try:
        if FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0].Faces[0] != []:
            if debug: print("With Selection")
            selObj = FreeCADGui.Selection.getSelectionEx()[0]
            obj.Face = selObj.Object, [selObj.SubElementNames[0]]
            obj.FaceMargin = 1
    except:
        if debug: print("No Selection")  
        obj.Height = 10
        obj.Width = 0
        obj.TextShape = "Faces"
        obj.TextShapeFusion = True
    obj.Text = ""
    font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.GeneralFont)
    obj.Font = font.toString()    
    obj.FontExt = etf.fontExtToString(font)
    if debug: print("easyTextGlyphs initPropertiesObject Ende")
    
class easyTextGlyphsFeature:
    def __init__(self, obj):
        debug = False
        if debug: print("easyTextGlyphsFeature __init__ Start")
        # Data Properties
        _tip = QT_TRANSLATE_NOOP("App::Property", "Your text")
        obj.addProperty("App::PropertyString", "Text", "Data", _tip)
        # eine String-Repräsentation des ausgewählten Fonts
        _tip = QT_TRANSLATE_NOOP("App::Property", "a string representation of the selected font")
        obj.addProperty("App::PropertyString", "Font", "Data", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "a string representation of extended font Attributes")
        obj.addProperty("App::PropertyString", "FontExt", "Data", _tip)
        obj.setPropertyStatus('Font', 'UserEdit')
        _tip = QT_TRANSLATE_NOOP("App::Property", "Output type")
        obj.addProperty("App::PropertyEnumeration", "TextShape", "Data", _tip)
        obj.TextShape = ["Wires", "Faces", "Extrusion"]
        obj.TextShape = "Wires"
        _tip = QT_TRANSLATE_NOOP("App::Property", "Extrusion Length")
        obj.addProperty("App::PropertyLength", "TextShapeExtrusion", "Data", _tip)
        obj.TextShapeExtrusion = 1
        obj.setPropertyStatus("TextShapeExtrusion", 'Hidden')
        _tip = QT_TRANSLATE_NOOP("App::Property", "Fuse TextShapes if possible")
        obj.addProperty("App::PropertyBool", "TextShapeFusion", "Data", _tip)
        obj.TextShapeFusion = False
        obj.setPropertyStatus("TextShapeFusion", 'Hidden')
        
        
        # Height Properties
        _tip = QT_TRANSLATE_NOOP("App::Property", "Height of text")
        obj.addProperty("App::PropertyLength", "Height", "Dimensions", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "if > 0, then it is the maximum allowed width for the specified text")
        obj.addProperty("App::PropertyLength", "Width", "Dimensions", _tip)
        
        # Sketch and Reference Properties
        _tip = QT_TRANSLATE_NOOP("App::Property", "Descender of the glyphs")
        obj.addProperty("App::PropertyFloatList", "DescenderList", "Reference", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "the sketch with the Text or the objects with the Shapes")
        obj.addProperty("App::PropertyLinkList", "Links", "Reference", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "if specified, then it is a face whose dimensions should be adopted for the text")
        obj.addProperty("App::PropertyLinkSub", "Face", "Reference", _tip)
        # Rand des Faces, der nicht für den Text zur Verfügung steht
        _tip = QT_TRANSLATE_NOOP("App::Property", "Margin of the face that is not available for text")
        obj.addProperty("App::PropertyLength", "FaceMargin", "Reference", _tip)
        initPropertiesObject(obj)
        obj.Proxy = self
        self.obj = obj        
        self.Type = "easyTextGlyphs"
        if debug: print("easyTextGlyphsFeature __init__ Ende")
    
    def execute(self, obj):
        debug = False
        if debug: print("easyTextGlyphsFeature execute Start")
        '''Do something when doing a recomputation, this method is mandatory'''
        redrawTextstring(obj)
        if debug: print("easyTextGlyphsFeature execute Ende")
        
    def onChanged(self, obj, prop):
        '''Do something when a property has changed'''
        debug = False
        if debug: print("easyTextGlyphsFeature onChanged Start")
        if debug: print("prop: " + str(prop))
        if prop == "TextShape":
            if debug: print("obj.TextShape: " + str(obj.TextShape))
            if hasattr(obj, 'TextShapeExtrusion'):
                if obj.TextShape == "Extrusion":
                    obj.setPropertyStatus("TextShapeExtrusion", '-Hidden')
                else:
                    obj.setPropertyStatus("TextShapeExtrusion", 'Hidden')
            if hasattr(obj, 'TextShapeFusion'):
                if obj.TextShape == "Wires":
                    obj.setPropertyStatus("TextShapeFusion", 'Hidden')
                else:
                    obj.setPropertyStatus("TextShapeFusion", '-Hidden')
        if debug: print("easyTextGlyphsFeature onChanged Ende")
        #redrawTextstring(obj)
        
    def editProperty(self, prop):
        debug = False
        if debug: print("easyTextGlyphsFeature editProperty Start")
        if prop == 'Font':
            if debug: print("self.obj.Text: " + str(self.obj.Text))
            if debug: print("self.obj.Font: " + str(self.obj.Font))
            qfont = QtGui.QFont()
            qfont.fromString(self.obj.Font)
            qfont = etf.fontExtFromString(qfont, self.obj.FontExt)
            form = dlgFormat.dlgFormat(qfont, self.obj.Text, "easyTextGlyphs")
            form.exec_()
            if form.result == "OK":
                if debug: print("text: " + str(form.getText()))
                if debug: print("form.qfont: " + str(form.qfont))
                qfont = form.qfont
                #qfont.setPointSize(36)
                self.obj.Font = form.qfont.toString()
                self.obj.Text = form.getText()
                self.obj.FontExt = etf.fontExtToString(form.qfont)
        if debug: print("easyTextGlyphsFeature editProperty Ende")
        
    def __getstate__(self):
        return None
        
    def __setstate__(self, data):
        return None


class easyTextGlyphsViewProvider:
    def __init__(self, vobj):
        '''Set this object to the proxy object of the actual view provider'''
        vobj.Proxy = self
        self.Object = vobj.Object
            
    def getIcon(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return os.path.join(etf.ICONPATH, 'etGlyphIcon.svg')

    def attach(self, vobj):
        '''Setup the scene sub-graph of the view provider, this method is mandatory'''
        self.Object = vobj.Object
        #self.onChanged(vobj, "Base")
        return
 
    def updateData(self, fp, prop):
        '''If a property of the handled feature has changed we have the chance to handle this here'''
        pass
    
    def claimChildren(self):
        '''Return a list of objects that will be modified by this feature'''
        return self.Object.Links
        
    def onDelete(self, feature, subelements):
        '''Here we can do something when the feature will be deleted'''
        return True
    
    def onChanged(self, fp, prop):
        '''Here we can do something when a single property got changed'''
        pass
        
    def startDefaultEditMode(self, viewObject):
        debug = False
        if debug:  print("easyTextGlyphsViewProvider startDefaultEditMode Start")
        document = viewObject.Document.Document
        print("document.HasPendingTransaction: " + str(document.HasPendingTransaction))
        if not document.HasPendingTransaction:
            if debug:  print("document.openTransaction")
            document.openTransaction("easyText")
        viewObject.Document.setEdit(viewObject.Object, 0)
        if debug:  print("easyTextGlyphsViewProvider startDefaultEditMode Ende")
        
    def setEdit(self, viewObject, mode):
        #self.panel = easyTextGlyphsTaskPanel(self.Object)
        #Gui.Control.showDialog(self.panel)
        #return True
        if mode == 0:
            FreeCADGui.Control.showDialog(easyTextGlyphsTaskPanel(viewObject))
            return True
            
    def unsetEdit(self, viewObject, mode):
        if mode == 0:
            FreeCADGui.Control.closeDialog()
            return True
        
    def __getstate__(self):
        '''When saving the document this object gets stored using Python's json module.\
                Since we have some un-serializable parts here -- the Coin stuff -- we must define this method\
                to return a tuple of all serializable objects or None.'''
        return None
 
    def __setstate__(self, state):
        '''When restoring the serialized object from document we have the chance to set some internals here.\
                Since no data were serialized nothing needs to be done here.'''
        return None
        
class easyTextGlyphsWidget(QtGui.QWidget):
    
    def __init__(self, obj, *args):
        debug = False
        if debug:  print("easyTextGlyphsWidget __init__ Start")
        QtGui.QWidget.__init__(self, *args)
        if debug:  print("obj: " + str(obj))
        self.obj = obj
        self.qfont = QtGui.QFont()
        self.qfont.fromString(self.obj.Font)
        self.form = None
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addLayout(self.__UI_Main__())
        if debug:  print("easyTextGlyphsWidget __init__ Ende")
        
    def __UI_Main__(self):
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.__UI_Text__())
        vbox.addLayout(self.__UI_Font__())
        vbox.addLayout(self.__UI_Dim__())
        vbox.addLayout(self.__UI_Shape__())        
        return vbox
        
    def __UI_Text__(self):
        hbox = QtGui.QHBoxLayout()
        self.text = QtGui.QLineEdit()
        self.text.setText(self.obj.Text)
        self.text.setPlaceholderText("Your Text here")
        self.text.setToolTip(self.obj.getDocumentationOfProperty("Text"))        
        hbox.addWidget(self.text)
        groupText = QtGui.QGroupBox("Text:")
        groupText.setLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()        
        hbox.addWidget(groupText)
        #hbox.addStretch()
        return hbox 

        
    def __UI_Font__(self):
        debug = False
        if debug:  print("easyTextGlyphsWidget __UI_Font__ Start")
        if debug:  print("self.obj.Font: " + str(self.obj.Font))
        hbox = QtGui.QHBoxLayout()
        self.cbFamily = QtGui.QFontComboBox()
        self.cbFamily.setCurrentFont(self.qfont)
        self.cbFamily.setToolTip(self.obj.getDocumentationOfProperty("Font"))
        self.cbFamily.currentFontChanged.connect(self.onFontComboChanged)
        hbox.addWidget(self.cbFamily)
        btn = QtGui.QPushButton('', self)
        icon = QtGui.QIcon(os.path.join(etf.ICONPATH, "Extended.svg").replace("\\", "/"))
        btn.setIcon(icon)
        btn.setToolTip("advanced settings")
        btn.clicked.connect(self.onAdvancedSettings)
        hbox.addWidget(btn)
        groupFamily = QtGui.QGroupBox("Font:")
        groupFamily.setLayout(hbox)
        #  erweiterte Einstellungen
        hbox = QtGui.QHBoxLayout()        
        hbox.addWidget(groupFamily)
        hbox.addStretch()
        if debug:  print("easyTextGlyphsWidget __UI_Font__ Ende")
        return hbox 
        
    def onFontComboChanged(self):
        debug = False
        if debug:  print("easyTextGlyphsWidget onFontComboChanged Start")
        if not self.form:
            self.qfont = QtGui.QFont()            
        self.qfont.setFamily(self.cbFamily.currentFont().family())
        #self.qfont.setPointSize(36)
        self.form = None
        if debug:  print("easyTextGlyphsWidget onFontComboChanged Ende")
        
    def onAdvancedSettings(self):
        debug = False
        if debug: print("easyTextGlyphsWidget onAdvancedSettings Start")
        if debug:  print("self: " + str(self))
        self.form = dlgFormat.dlgFormat(self.qfont, self.text.text(), "easyTextGlyphs")
        self.form.exec_()
        if self.form.result == "OK":
            self.qfont = self.form.qfont
            self.text.setText(self.form.getText())
            self.cbFamily.setCurrentFont(self.qfont)
        if debug: print("easyTextGlyphsWidget onAdvancedSettings Ende")
        
    def __UI_Dim__(self):
        debug = False
        if debug:  print("easyTextGlyphsWidget __UI_Dim__ Start")
        if debug:  print("self.obj.Height: " + str(self.obj.Height))
        if debug:  print("self.obj.Width: " + str(self.obj.Width))
        hbox = QtGui.QHBoxLayout()
        self.uiHeight = QtGui.QLineEdit()
        self.uiHeight.setValidator(QtGui.QDoubleValidator())
        self.uiHeight.setText(str(float(self.obj.Height)))
        #self.uiHeight.setValue(int(self.obj.Height))
        self.uiHeight.setToolTip(self.obj.getDocumentationOfProperty("Height"))
        hbox.addWidget(self.uiHeight)
        groupHeight = QtGui.QGroupBox("Height:")
        groupHeight.setLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        self.uiWidth = QtGui.QLineEdit()
        #self.uiWidth.setValue(int(self.obj.Width))
        self.uiWidth.setValidator(QtGui.QDoubleValidator())
        self.uiWidth.setText(str(float(self.obj.Width)))
        self.uiWidth.setToolTip(self.obj.getDocumentationOfProperty("Width"))
        hbox.addWidget(self.uiWidth)
        groupWidth = QtGui.QGroupBox("Width:")
        groupWidth.setLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()        
        hbox.addWidget(groupHeight)
        hbox.addWidget(groupWidth)
        hbox.addStretch()
        if debug:  print("easyTextGlyphsWidget __UI_Dim__ Ende")
        return hbox 
        
    def __UI_Shape__(self):
        debug = False
        if debug:  print("easyTextGlyphsWidget __UI_Shape__ Start")
        if debug:  print("self.obj.TextShape: " + str(self.obj.TextShape))
        hbox = QtGui.QHBoxLayout()
        self.cbShape = QtGui.QComboBox()
        options = self.obj.getEnumerationsOfProperty("TextShape")
        self.cbShape.addItems(options)
        self.cbShape.setCurrentText(self.obj.TextShape)
        self.cbShape.setToolTip(self.obj.getDocumentationOfProperty("TextShape"))
        self.cbShape.currentIndexChanged[int].connect(self.onShapeChanged)
        hbox.addWidget(self.cbShape)
        groupShape = QtGui.QGroupBox("TextShape:")
        groupShape.setLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        self.leExtHeight = QtGui.QLineEdit()
        self.leExtHeight.setValidator(QtGui.QDoubleValidator())
        # self.uiHeight.setValue(int(self.obj.Height))
        self.leExtHeight.setText(str(float(self.obj.TextShapeExtrusion)))
        self.leExtHeight.setToolTip(self.obj.getDocumentationOfProperty("TextShapeExtrusion"))
        hbox.addWidget(self.leExtHeight)
        self.groupExtHeight = QtGui.QGroupBox("ExtrusionHeight:")
        self.groupExtHeight.setLayout(hbox)
        if self.cbShape.currentText() != "Extrusion":
            self.groupExtHeight.hide()
            
        hbox = QtGui.QHBoxLayout()
        self.chkFusion = QtGui.QCheckBox()
        self.chkFusion.setChecked(self.obj.TextShapeFusion)
        self.chkFusion.setToolTip(self.obj.getDocumentationOfProperty("TextShapeFusion"))
        hbox.addWidget(self.chkFusion)
        self.groupFuseFaces = QtGui.QGroupBox("Fusion:")
        self.groupFuseFaces.setLayout(hbox)
        if self.cbShape.currentText() == "Wires":
            self.groupFuseFaces.hide()
        
        hbox = QtGui.QHBoxLayout()        
        hbox.addWidget(groupShape)
        hbox.addWidget(self.groupExtHeight)
        hbox.addWidget(self.groupFuseFaces)
        hbox.addStretch()
        if debug:  print("easyTextGlyphsWidget __UI_Shape__ Ende")
        return hbox 
        
    def onShapeChanged(self):
        debug = False
        if debug:  print("easyTextGlyphsWidget onShapeChanged Start")
        if debug:  print("shape: " + str(self.sender().currentText()))
        if self.sender().currentText() == "Extrusion":
            self.groupExtHeight.show()
        else:
            self.groupExtHeight.hide()
        if self.sender().currentText() != "Wires":
            self.groupFuseFaces.show()
        else:
            self.groupFuseFaces.hide()
        if debug:  print("easyTextGlyphsWidget onShapeChanged Ende")
    
        
class easyTextGlyphsTaskPanel:
    def __init__(self, viewObject):
        debug = False
        if debug: print("easyTextGlyphsTaskPanel __init__ Start")
        self.viewObject = viewObject
        self.form = easyTextGlyphsWidget(self.viewObject.Object)
        if debug: print("easyTextGlyphsTaskPanel __init__ Ende")

    def accept(self):
        debug = False
        if debug: print("easyTextGlyphsTaskPanel accept Start")
        '''called when the OK button in the task panel is pressed'''        
        obj = self.viewObject.Object
        if not obj.isValid():
            QtGui.QMessageBox.warning(None, "Error", obj.getStatusString())
            return False
        obj.Text = self.form.text.text()
        #if debug: print("obj.Text: " + str(obj.Text))
        obj.Height = float(self.form.uiHeight.text())
        #obj.Height = self.form.uiHeight.value()
        #if debug: print("obj.Height: " + str(obj.Height))
        #obj.Width = self.form.uiWidth.value()
        obj.Width = float(self.form.uiWidth.text())
        obj.TextShape = self.form.cbShape.currentText()
        obj.TextShapeExtrusion = float(self.form.leExtHeight.text())
        obj.TextShapeFusion = bool(self.form.chkFusion.checkState())
        obj.Font = self.form.qfont.toString()
        redrawTextstring(obj)
        document = self.viewObject.Document.Document
        if debug:  print("document.commitTransaction")
        document.commitTransaction()
        document.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        if debug: print("easyTextGlyphsTaskPanel accept Ende")
        return True
        
    def reject(self):
        debug = False
        if debug: print("easyTextGlyphsTaskPanel reject Start")
        '''called when the Cancel button in the task panel is pressed'''
        guidocument = self.viewObject.Document
        document = guidocument.Document
        if debug:  print("document.abortTransaction")
        document.abortTransaction()
        document.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        if debug: print("easyTextGlyphsTaskPanel reject Ende")
        return True
   

        
       
def redrawTextstring(obj):
    debug = False
    if debug: print("easyTextGlyphs redrawTextstring Start")
    if obj.Text != "":
        executeObject(obj)
    if debug: print("obj.Font: " + str(obj.Font))    
    if debug: print("obj.Text: " + str(obj.Text))
    #if debug: print("self.obj.LinkListGlyphs: " + str(self.obj.LinkListGlyphs))
    if debug: print("easyTextGlyphs redrawTextstring Ende")
    

    
        
class CommandeasyTextGlyphs():
    """Command for creating easyTextGlyphs"""    
                
    def GetResources(self):
        return {'Pixmap'  : os.path.join(etf.ICONPATH, 'etGlyphIcon.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': "easyTextGlyphs",
                'ToolTip' : __doc__ }
      
    def Activated(self):
        debug = False
        if debug:  print("CommandeasyTextGlyphs Activated Start")
        if len(FreeCAD.listDocuments()) == 0:
            FreeCAD.Console.PrintError(translate("easyText", "No active document") + "\n")
            return None
        if debug:  print("document.openTransaction")
        FreeCAD.ActiveDocument.openTransaction("easyText")
        obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "easyTextGlyphs")
        easyTextGlyphsFeature(obj)
        vp = easyTextGlyphsViewProvider(obj.ViewObject)
        FreeCAD.ActiveDocument.recompute()
        vp.startDefaultEditMode(obj.ViewObject)
        if debug:  print("CommandeasyTextGlyphs Activated Ende")


FreeCADGui.addCommand('easyTextGlyphs', CommandeasyTextGlyphs())
