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
import easyTextGlyphs

__dir__ = os.path.dirname(__file__)
__iconpath__ = os.path.join(__dir__, 'etTextRevolveIcon.svg')


def executeObject(obj):
    debug = True
    if debug:  print("easyTextRevolve executeObject Start")
    if debug:  print("obj.TextObject: " + str(obj.TextObject))
    if obj.TextObject:
        tobj = obj.TextObject
        degree = obj.Degree
        forceBaseline = obj.ForceBaseline
        sunken = obj.Sunken
        makeBase = obj.MakeBase
        baseHeight = obj.BaseHeight
        baseAddX = obj.BaseAddX
        baseAddY = obj.BaseAddY
        baseCornerFilletRadius = obj.BaseCornerFilletRadius
        baseTopFilletRadius = obj.BaseTopFilletRadius
        rshape = etf.makeGlyphRevolve(tobj, degree, forceBaseline, sunken, makeBase, baseHeight, baseAddX, baseAddY, baseCornerFilletRadius, baseTopFilletRadius)
        if rshape:
            obj.Shape = rshape
    if debug:  print("easyTextRevolve executeObject Ende")

def initPropertiesObject(obj):
    debug = False
    if debug: print("easyTextRevolve initPropertiesObject Start")
    obj.TextObject = None
    obj.Degree = 50
    obj.ForceBaseline = False
    obj.Sunken = 0.0
    obj.MakeBase = True
    obj.BaseHeight = 5.0
    obj.BaseAddX = 10.0
    obj.BaseAddY = 10.0
    obj.BaseCornerFilletRadius = 5.0
    obj.BaseTopFilletRadius = 1.0
    for sel in FreeCADGui.Selection.getSelection():
        if debug: print("sel.Name: " + str(sel.Name))
        try:
            if isinstance(sel.Proxy, easyTextGlyphs.easyTextGlyphsFeature):
                if debug:  print("Text")
                obj.TextObject = sel
        except:
            pass
    if debug: print("easyTextRevolve initPropertiesObject Ende")
    
class easyTextRevolveFeature:
    def __init__(self, obj):
        debug = False
        if debug: print("easyTextRevolveFeature __init__ Start")
        # Data Properties
        _tip = QT_TRANSLATE_NOOP("App::Property", "easyTextGlyphs Object")
        obj.addProperty("App::PropertyLink", "TextObject", "Data", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "Degrees of the Revolution.")
        obj.addProperty("App::PropertyInteger", "Degree", "Data", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "A revolve of an easyTextGlyph is only possible if the lowest point of no letter lies below the baseline. Minor deviations can be corrected with ForceBaseline, but this may affect the visual appearance of the font.")
        obj.addProperty("App::PropertyBool", "ForceBaseline", "Data", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "Causes the shape to sink into the base.")
        obj.addProperty("App::PropertyLength", "Sunken", "Data", _tip)
        
        _tip = QT_TRANSLATE_NOOP("App::Property", "Make Base for Revolution")
        obj.addProperty("App::PropertyBool", "MakeBase", "Extension", _tip)        
        _tip = QT_TRANSLATE_NOOP("App::Property", "Height of the Base")
        obj.addProperty("App::PropertyLength", "BaseHeight", "Extension", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "Extension of the Base in X-Direction, half of the specified value on each side.")
        obj.addProperty("App::PropertyLength", "BaseAddX", "Extension", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "Extension of the Base in Y-Direction, half of the specified value on each side.")
        obj.addProperty("App::PropertyLength", "BaseAddY", "Extension", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "Fillet of the corner-edges.")
        obj.addProperty("App::PropertyLength", "BaseCornerFilletRadius", "Extension", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "Fillet of the top-edge.")
        obj.addProperty("App::PropertyLength", "BaseTopFilletRadius", "Extension", _tip)
        
        initPropertiesObject(obj)
        obj.Proxy = self
        self.obj = obj        
        self.Type = "easyTextRevolve"
        if debug: print("easyTextRevolveFeature __init__ Ende")
    
    def execute(self, obj):
        redrawRevolution(obj)
        
    def onChanged(self, obj, prop):
        debug = False
        if debug: print("easyTextRevolveFeature onChanged Start")
        if debug: print("prop: " + str(prop))
        if debug: print("easyTextRevolveFeature onChanged Ende")
        
    def editProperty(self, prop):
        debug = False
        if debug: print("easyTextRevolveFeature editProperty Start")
        if debug: print("easyTextRevolveFeature editProperty Ende")
        
    def __getstate__(self):
        return None
        
    def __setstate__(self, data):
        return None


class easyTextRevolveViewProvider:
    def __init__(self, vobj):
        vobj.Proxy = self
        self.Object = vobj.Object
            
    def getIcon(self):
        return os.path.join(etf.ICONPATH, 'etTextOnPathIcon.svg')

    def attach(self, vobj):
        self.Object = vobj.Object
        return
 
    def updateData(self, fp, prop):
        pass
    
    def claimChildren(self):
        return [self.Object.TextObject]
        
    def onDelete(self, feature, subelements):
        return True
    
    def onChanged(self, fp, prop):
        pass
        
    def startDefaultEditMode(self, viewObject):
        debug = False
        if debug: print("easyTextRevolveViewProvider startDefaultEditMode Start")
        document = viewObject.Document.Document
        print("document.HasPendingTransaction: " + str(document.HasPendingTransaction))
        if not document.HasPendingTransaction:
            if debug:  print("document.openTransaction")
            document.openTransaction("easyText")
        viewObject.Document.setEdit(viewObject.Object, 0)
        if debug: print("easyTextRevolveViewProvider startDefaultEditMode Ende")
        
    def setEdit(self, viewObject, mode):
        if mode == 0:
            FreeCADGui.Control.showDialog(easyTextRevolveTaskPanel(viewObject))
            return True 
            
    def unsetEdit(self, viewObject, mode):
        viewObject.show()
        document = viewObject.Document.Document
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
        
class easyTextRevolveWidget(QtGui.QWidget):
    
    def __init__(self, obj, *args):
        debug = False
        if debug:  print("easyTextRevolveWidget __init__ Start")
        QtGui.QWidget.__init__(self, *args)
        if debug:  print("obj: " + str(obj))
        if debug:  print("obj.TextObject: " + str(obj.TextObject))
        self.obj = obj
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addLayout(self.__UI_Main__())
        #self.closeEvent = self.onClose()
        if debug:  print("easyTextRevolveWidget __init__ Ende")
        
    def __UI_Main__(self):
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.__UI_TextObject__())
        vbox.addLayout(self.__UI_Attributes__())
        return vbox
        
    def __UI_TextObject__(self):
        debug = False
        if debug: print("easyTextRevolveWidget __UI_TextObject__ Start")   
        hbox = QtGui.QHBoxLayout()
        options = etf.getGlyphObjects()
        if debug: print("options: " + str(options))
        self.cbText = QtGui.QComboBox()        
        self.cbText.addItems(options)
        if self.obj.TextObject:
            self.cbText.setCurrentText(self.obj.TextObject.Label)
        self.cbText.setToolTip("select a easyTextGlyph-Object")
        hbox.addWidget(self.cbText)
        group = QtGui.QGroupBox("TextObject:")
        group.setLayout(hbox)
        hbox = QtGui.QHBoxLayout()        
        hbox.addWidget(group)
        if debug: print("easyTextRevolveWidget __UI_TextObject__ Ende")
        return hbox 

    def __UI_Attributes__(self):
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.__UI_Revolve__())
        vbox.addLayout(self.__UI_Base__())
        return vbox
        
    def __UI_Revolve__(self):
        hbox = QtGui.QHBoxLayout()
        self.Degree = QtGui.QSpinBox()
        self.Degree.setValue(self.obj.Degree)
        hbox.addWidget(self.Degree)
        groupdegree = QtGui.QGroupBox("Degree:")
        groupdegree.setLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        self.chkForce = QtGui.QCheckBox()
        self.chkForce.setChecked(self.obj.ForceBaseline)
        self.chkForce.setToolTip(self.obj.getDocumentationOfProperty("ForceBaseline"))
        hbox.addWidget(self.chkForce)
        groupforce = QtGui.QGroupBox("Force Baseline:")
        groupforce.setLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        self.Sunken = QtGui.QLineEdit()
        self.Sunken.setValidator(QtGui.QDoubleValidator())
        self.Sunken.setText(str(float(self.obj.Sunken)))
        self.Sunken.setToolTip(self.obj.getDocumentationOfProperty("Sunken"))
        hbox.addWidget(self.Sunken)
        groupsunken = QtGui.QGroupBox("Sunken:")
        groupsunken.setLayout(hbox)
        
        vbox = QtGui.QVBoxLayout()        
        vbox.addWidget(groupdegree)
        vbox.addWidget(groupforce)
        vbox.addWidget(groupsunken)
        return vbox         
        
    def __UI_Base__(self):
        debug = False
        if debug: print("easyTextRevolveWidget __UI_Base__ Start")   
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.__UI_Attr_BaseHeight__())
        vbox.addLayout(self.__UI_Attr_BaseAdd__())
        vbox.addLayout(self.__UI_Attr_BaseFillet__())
        self.makeBase = QtGui.QGroupBox("Make Base:")
        self.makeBase.setLayout(vbox)
        self.makeBase.setCheckable(True)
        self.makeBase.setChecked(self.obj.MakeBase)
        self.makeBase.toggled.connect(self.onToggleGroup)
        if debug: print("self.sizeHint(): " + str(self.sizeHint()))
        if self.makeBase.isChecked():
            self.makeBase.setFixedHeight(self.makeBase.sizeHint().height())
        else:
            self.makeBase.setFixedHeight(30)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.makeBase)
        if debug: print("easyTextRevolveWidget __UI_Base__ Ende")
        return vbox
        
    def onToggleGroup(self):
        debug = False
        if debug: print("fontFormatWidget onToggleGroup Start")        
        group = self.sender()
        if group.isChecked():
            group.setFixedHeight(group.sizeHint().height())
        else:
            group.setFixedHeight(30)
        if debug: print("fontFormatWidget onToggleGroup Ende")
        
    def __UI_Attr_BaseHeight__(self):
        hbox = QtGui.QHBoxLayout()
        self.BaseHeight = QtGui.QLineEdit()
        self.BaseHeight.setValidator(QtGui.QDoubleValidator())
        self.BaseHeight.setText(str(float(self.obj.BaseHeight)))
        self.BaseHeight.setToolTip(self.obj.getDocumentationOfProperty("BaseHeight"))
        hbox.addWidget(self.BaseHeight)
        groupBaseHeight = QtGui.QGroupBox("BaseHeight:")
        groupBaseHeight.setLayout(hbox)
        
        vbox = QtGui.QVBoxLayout()        
        vbox.addWidget(groupBaseHeight)
        return vbox                 
        
    def __UI_Attr_BaseAdd__(self):
        hbox = QtGui.QHBoxLayout()
        self.BaseAddX = QtGui.QLineEdit()
        self.BaseAddX.setValidator(QtGui.QDoubleValidator())
        self.BaseAddX.setText(str(float(self.obj.BaseAddX)))
        self.BaseAddX.setToolTip(self.obj.getDocumentationOfProperty("BaseAddX"))
        hbox.addWidget(self.BaseAddX)
        groupAddX = QtGui.QGroupBox("Base Add X:")
        groupAddX.setLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        self.BaseAddY = QtGui.QLineEdit()
        self.BaseAddY.setValidator(QtGui.QDoubleValidator())
        self.BaseAddY.setText(str(float(self.obj.BaseAddY)))
        self.BaseAddY.setToolTip(self.obj.getDocumentationOfProperty("BaseAddY"))
        hbox.addWidget(self.BaseAddY)
        groupAddY = QtGui.QGroupBox("Base Add Y:")
        groupAddY.setLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()        
        hbox.addWidget(groupAddX)
        hbox.addWidget(groupAddY)
        return hbox                 
        
    def __UI_Attr_BaseFillet__(self):
        hbox = QtGui.QHBoxLayout()
        self.BaseCornerFil = QtGui.QLineEdit()
        self.BaseCornerFil.setValidator(QtGui.QDoubleValidator())
        self.BaseCornerFil.setText(str(float(self.obj.BaseCornerFilletRadius)))
        self.BaseCornerFil.setToolTip(self.obj.getDocumentationOfProperty("BaseCornerFilletRadius"))
        hbox.addWidget(self.BaseCornerFil)
        groupCFil = QtGui.QGroupBox("Base Corner Fillet Radius:")
        groupCFil.setLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        self.BaseTopFil = QtGui.QLineEdit()
        self.BaseTopFil.setValidator(QtGui.QDoubleValidator())
        self.BaseTopFil.setText(str(float(self.obj.BaseTopFilletRadius)))
        self.BaseTopFil.setToolTip(self.obj.getDocumentationOfProperty("BaseTopFilletRadius"))
        hbox.addWidget(self.BaseTopFil)
        groupTFil = QtGui.QGroupBox("Base Top Fillet Radius:")
        groupTFil.setLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()        
        hbox.addWidget(groupCFil)
        hbox.addWidget(groupTFil)
        return hbox                 
    
        
class easyTextRevolveTaskPanel:
    def __init__(self, viewObject):
        debug = False
        if debug: print("easyTextRevolveTaskPanel __init__ Start")
        self.viewObject = viewObject
        self.form = easyTextRevolveWidget(self.viewObject.Object)
        #self.closeEvent = self.onClose()
        if debug: print("easyTextRevolveTaskPanel __init__ Ende")

    def accept(self):
        debug = False
        if debug: print("easyTextRevolveTaskPanel accept Start")
        FreeCAD.Gui.updateGui()
        try:
            FreeCAD.ActiveDocument.removeObject("etPreviewTaP")
        except:
            pass
        '''called when the OK button in the task panel is pressed'''        
        obj = self.viewObject.Object
        if not obj.isValid():
            QtGui.QMessageBox.warning(None, "Error", obj.getStatusString())
            return False
        obj.TextObject = FreeCAD.ActiveDocument.getObjectsByLabel(self.form.cbText.currentText())[0]
        if debug: print("obj.TextObject: " + str(obj.TextObject))
        obj.Degree = self.form.Degree.value()
        if debug: print("obj.Degree: " + str(obj.Degree))
        obj.Sunken = float(self.form.Sunken.text())
        obj.MakeBase = self.form.makeBase.isChecked()
        obj.BaseHeight = float(self.form.BaseHeight.text())
        obj.BaseAddX = float(self.form.BaseAddX.text())
        obj.BaseAddY = float(self.form.BaseAddY.text())
        obj.BaseCornerFilletRadius = float(self.form.BaseCornerFil.text())
        obj.BaseTopFilletRadius = float(self.form.BaseTopFil.text())
        redrawRevolution(obj)
        obj.TextObject.ViewObject.hide()
        document = self.viewObject.Document.Document
        if debug:  print("document.commitTransaction")
        document.commitTransaction()
        document.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        if debug: print("easyTextRevolveTaskPanel accept Ende")
        return True
        
    def reject(self):
        debug = False
        if debug:  print("easyTextRevolveTaskPanel reject Start")
        FreeCAD.Gui.updateGui()
        try:
            FreeCAD.ActiveDocument.removeObject("etPreviewTaP")
        except:
            pass
        '''called when the Cancel button in the task panel is pressed'''
        guidocument = self.viewObject.Document
        document = guidocument.Document
        if debug:  print("document.abortTransaction")
        document.abortTransaction()
        document.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        if debug:  print("easyTextRevolveTaskPanel reject Ende")
        return True
   

def redrawRevolution(obj):
    debug = False
    if debug: print("easyTextRevolve redrawRevolution Start")
    executeObject(obj)
    if debug: print("obj.Font: " + str(obj.Font))    
    if debug: print("obj.Text: " + str(obj.Text))
    if debug: print("easyTextRevolve redrawRevolution Ende")
    

    
        
class CommandEasyTextRevolve():
    """Command for creating easyTextRevolve"""    
                
    def GetResources(self):
        return {'Pixmap'  : os.path.join(etf.ICONPATH, 'etTextRevolveIcon.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': "easyTextRevolve",
                'ToolTip' : __doc__ }
      
    def Activated(self):
        debug = False
        if debug:  print("CommandEasyTextRevolve Activated Start")
        if len(FreeCAD.listDocuments()) == 0:
            FreeCAD.Console.PrintError(translate("easyText", "No active document") + "\n")
            return None
        FreeCAD.ActiveDocument.openTransaction("easyText")
        obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "easyTextRevolve")
        easyTextRevolveFeature(obj)
        vp = easyTextRevolveViewProvider(obj.ViewObject)
        FreeCAD.ActiveDocument.recompute()
        vp.startDefaultEditMode(obj.ViewObject)
        if debug:  print("CommandEasyTextRevolve Activated Ende")


FreeCADGui.addCommand('easyTextRevolve', CommandEasyTextRevolve())
