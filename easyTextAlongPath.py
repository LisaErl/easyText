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
import etFuncText2Path as etp
import easyTextGlyphs

__dir__ = os.path.dirname(__file__)
__iconpath__ = os.path.join(__dir__, 'etTextOnPathIcon.svg')


def executeObject(obj):
    debug = True
    if debug:  print("easyTextAlongPath executeObject Start")
    if debug:  print("obj: " + str(obj.Name))
    if not obj.WireObject or not obj.TextObject:
        if debug:  print("easyTextAlongPath executeObject Ende")
        return
    if debug:  print("obj.WireObject: " + str(obj.WireObject.Name))    
    if debug:  print("obj.WireObject.Placement: " + str(obj.WireObject.Placement))
    if debug:  print("obj.TextObject: " + str(obj.TextObject.Name))
    if debug:  print("obj.Distance: " + str(obj.Distance))
    if debug:  print("obj.Position: " + str(obj.Position))
    if debug:  print("obj.CenterAt: " + str(obj.CenterAt))
    if obj.WireObject and obj.TextObject:
        wire = obj.WireObject.Shape

        textshape = obj.TextObject.Shape
        descenderList = obj.TextObject.DescenderList
        offset = float(obj.Distance)
        pathShape = etp.makeGlyph2Path(wire, textshape, descenderList, centerAt = obj.CenterAt, position = obj.Position, offset = offset)
        if pathShape:
            obj.Shape = pathShape
    else:
        if debug:  print("Nothing to do: Wire or Text missing")
    if debug:  print("easyTextAlongPath executeObject Ende")
    
def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
           child.widget().deleteLater()

def initPropertiesObject(obj):
    debug = False
    if debug: print("easyTextAlongPath initPropertiesObject Start")
    obj.TextObject = None
    obj.WireObject = None
    obj.Distance = 0.0
    obj.CenterAt = "Center"
    obj.Position = "Above"
    obj.AdjustingLength = "None"
    for sel in FreeCADGui.Selection.getSelection():
        if debug: print("sel: " + str(sel))
        if debug: print("sel.Name: " + str(sel.Name))
        try:
            if isinstance(sel.Proxy, easyTextGlyphs.easyTextGlyphsFeature):
                if debug:  print("Text")
                obj.TextObject = sel
        except:
            if isinstance(sel.Shape, Part.Wire,):
                if debug:  print("Wire")
                obj.WireObject = sel
                if obj.WireObject.Shape.isClosed():
                    obj.CenterAt = "Top"
                    obj.Position = "Outside"        
    if debug: print("easyTextAlongPath initPropertiesObject Ende")
    
class easyTextAlongPathFeature:
    def __init__(self, obj):
        debug = False
        if debug: print("easyTextAlongPathFeature __init__ Start")
        # Data Properties
        _tip = QT_TRANSLATE_NOOP("App::Property", "Text Object")
        obj.addProperty("App::PropertyLink", "TextObject", "Data", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "Wire Object")
        obj.addProperty("App::PropertyLink", "WireObject", "Data", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "Distance between wire and text in mm")
        obj.addProperty("App::PropertyLength", "Distance", "Data", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "Position of the text relative to the wire")
        obj.addProperty("App::PropertyString", "Position", "Data", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "Center for Text")
        obj.addProperty("App::PropertyString", "CenterAt", "Data", _tip)
        _tip = QT_TRANSLATE_NOOP("App::Property", "Adjusting the length of text and wire")
        obj.addProperty("App::PropertyString", "AdjustingLength", "Data", _tip)
        initPropertiesObject(obj)
        obj.Proxy = self
        self.obj = obj        
        self.Type = "easyTextAlongPath"
        if debug: print("easyTextAlongPathFeature __init__ Ende")
    
    def execute(self, obj):
        '''Do something when doing a recomputation, this method is mandatory'''
        redrawTextstring(obj)
        
    def onChanged(self, obj, prop):
        '''Do something when a property has changed'''
        debug = False
        if debug: print("easyTextAlongPathFeature onChanged Start")
        if debug: print("prop: " + str(prop))
        if debug: print("easyTextAlongPathFeature onChanged Ende")
        
    def editProperty(self, prop):
        debug = False
        if debug: print("easyTextAlongPathFeature editProperty Start")
        if debug: print("easyTextAlongPathFeature editProperty Ende")
        
    def __getstate__(self):
        return None
        
    def __setstate__(self, data):
        return None


class easyTextAlongPathViewProvider:
    def __init__(self, vobj):
        '''Set this object to the proxy object of the actual view provider'''
        vobj.Proxy = self
        self.Object = vobj.Object
            
    def getIcon(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return os.path.join(etf.ICONPATH, 'etTextOnPathIcon.svg')

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
        return [self.Object.TextObject, self.Object.WireObject]
        
    def onDelete(self, feature, subelements):
        '''Here we can do something when the feature will be deleted'''
        return True
    
    def onChanged(self, fp, prop):
        '''Here we can do something when a single property got changed'''
        pass
        
    def startDefaultEditMode(self, viewObject):
        debug = False
        if debug: print("easyTextAlongPathViewProvider startDefaultEditMode Start")
        document = viewObject.Document.Document
        print("document.HasPendingTransaction: " + str(document.HasPendingTransaction))
        if not document.HasPendingTransaction:
            if debug:  print("document.openTransaction")
            document.openTransaction("easyText")
        viewObject.Document.setEdit(viewObject.Object, 0)
        if debug: print("easyTextAlongPathViewProvider startDefaultEditMode Ende")
        
    def setEdit(self, viewObject, mode):
        if mode == 0:
            FreeCADGui.Control.showDialog(easyTextAlongPathTaskPanel(viewObject))
            return True 
            
    def unsetEdit(self, viewObject, mode):
        viewObject.show()
        #FreeCAD.Gui.updateGui()
        document = viewObject.Document.Document
        try:
            FreeCAD.ActiveDocument.removeObject("etPreviewTaP")
        except:
            pass
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
        
class easyTextAlongPathWidget(QtGui.QWidget):
    
    def __init__(self, obj, *args):
        debug = False
        if debug:  print("easyTextAlongPathWidget __init__ Start")
        QtGui.QWidget.__init__(self, *args)
        if debug:  print("obj: " + str(obj))
        if debug:  print("obj.WireObject: " + str(obj.WireObject))
        if debug:  print("obj.TextObject: " + str(obj.TextObject))
        self.obj = obj
        self.wireObj = None
        self.prevObj = None
        self.preview = False
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addLayout(self.__UI_Main__())
        #self.closeEvent = self.onClose()
        if debug:  print("easyTextAlongPathWidget __init__ Ende")
        
    def __UI_Main__(self):
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.__UI_TextObject__())
        vbox.addLayout(self.__UI_WireObject__())
        vbox.addLayout(self.__UI_Attributes__())
        return vbox
        
    def __UI_TextObject__(self):
        debug = False
        if debug: print("easyTextAlongPathWidget __UI_TextObject__ Start")        
        hbox = QtGui.QHBoxLayout()
        options = etf.getGlyphObjects()
        if debug: print("options: " + str(options))
        if debug: print("options: " + str(options))
        self.cbText = QtGui.QComboBox()        
        self.cbText.addItems(options)
        if self.obj.TextObject:
            self.cbText.setCurrentText(self.obj.TextObject.Label)
        self.cbText.setToolTip("select a easyTextGlyph-Object")
        self.cbText.currentIndexChanged[int].connect(self.showPreview)
        hbox.addWidget(self.cbText)
        group = QtGui.QGroupBox("TextObject:")
        group.setLayout(hbox)
        hbox = QtGui.QHBoxLayout()        
        hbox.addWidget(group)
        if debug: print("easyTextAlongPathWidget __UI_TextObject__ Ende")
        return hbox 

    def __UI_WireObject__(self):
        debug = False
        if debug:  print("easyTextAlongPathWidget __UI_WireObject__ Start")
        hbox = QtGui.QHBoxLayout()
        self.cbWire = QtGui.QComboBox()        
        options = etf.getWireObjects()
        self.cbWire.addItems(options)
        if self.obj.WireObject:
            self.cbWire.setCurrentText(self.obj.WireObject.Label)
        self.cbWire.setToolTip("select a easyTextGlyph-Object")
        self.cbWire.currentIndexChanged[int].connect(self.onWireChanged)
        if debug:  print("self.cbWire.currentText(): " + str(self.cbWire.currentText()))
        if self.cbWire.currentText() != "":
            self.wireObj = FreeCAD.ActiveDocument.getObjectsByLabel(self.cbWire.currentText())[0]
        hbox.addWidget(self.cbWire)
        group = QtGui.QGroupBox("WireObject:")
        group.setLayout(hbox)
        hbox = QtGui.QHBoxLayout()        
        hbox.addWidget(group)
        if debug:  print("easyTextAlongPathWidget __UI_WireObject__ Ende")
        return hbox         
        
    def onWireChanged(self):
        debug = False
        if debug:  print("easyTextAlongPathWidget onWireChanged Start")
        if debug:  print("wire: " + str(self.sender().currentText()))
        self.wireObj = FreeCAD.ActiveDocument.getObjectsByLabel(self.sender().currentText())[0]
        clearLayout(self.posbox)
        self.setPosBtn(self.posbox)
        clearLayout(self.ctrbox)
        self.setCtrBtn(self.ctrbox)
        self.showPreview()
        if debug:  print("easyTextAlongPathWidget onWireChanged Ende")

    def __UI_Attributes__(self):
        vbox = QtGui.QVBoxLayout()
        hbox = QtGui.QHBoxLayout()        
        hbox.addLayout(self.__UI_Attr_Position__())
        hbox.addLayout(self.__UI_Attr_CenterAt__())
        vbox.addLayout(hbox)
        vbox.addLayout(self.__UI_Attr_Distance__())
        vbox.addLayout(self.__UI_Attr_Preview__())
        return vbox
        
    def getClosed(self):
        closed = False
        if self.wireObj:
            if self.wireObj.Shape.isClosed():
                closed = True
        return closed
        
    def __UI_Attr_CenterAt__(self):
        self.ctrbox = QtGui.QHBoxLayout()
        self.setCtrBtn(self.ctrbox)
        return self.ctrbox
        
    def setCtrBtn(self, xbox):
        debug = False
        if debug:  print("easyTextAlongPathWidget setCtrBtn Start")
        hbox = QtGui.QHBoxLayout()
        options = ["Center"]
        isClosed = self.getClosed()
        if isClosed:
            options = ["Top", "Bottom"]
        self.ctrGroup = QtGui.QButtonGroup()
        self.ctrGroup.setExclusive(True)
        for i1, name in enumerate(options):
            btn = QtGui.QRadioButton(name)
            btn.clicked.connect(self.showPreview)
            if i1 == 0:
                btn.setChecked(True)
            hbox.addWidget(btn)
            self.ctrGroup.addButton(btn)
        hbox.addStretch()
        group = QtGui.QGroupBox("CenterAt:")
        group.setLayout(hbox)
        if not isClosed:
            group.hide()
        xbox.addWidget(group)
        if debug:  print("easyTextAlongPathWidget setCtrBtn Ende")

    def getCenterAt(self):
        debug = False
        if debug:  print("easyTextAlongPathWidget getPosition Start")
        btn = self.ctrGroup.checkedButton()
        if debug:  print("easyTextAlongPathWidget getPosition Start")
        return btn.text()
        
    def __UI_Attr_Position__(self):
        self.posbox = QtGui.QHBoxLayout()
        self.setPosBtn(self.posbox)
        return self.posbox
        
    def setPosBtn(self, xbox):
        hbox = QtGui.QHBoxLayout()
        options = ["Above", "Below"]
        isClosed = self.getClosed()
        if isClosed:
            options = ["Outside", "Inside"]
        self.posGroup = QtGui.QButtonGroup()
        self.posGroup.setExclusive(True)
        for i1, name in enumerate(options):
            btn = QtGui.QRadioButton(name)
            btn.clicked.connect(self.showPreview)
            if i1 == 0:
                btn.setChecked(True)
            hbox.addWidget(btn)
            self.posGroup.addButton(btn)
        hbox.addStretch()
        group = QtGui.QGroupBox("Position:")
        group.setLayout(hbox)
        xbox.addWidget(group)
        
    def getPosition(self):
        debug = False
        if debug:  print("easyTextAlongPathWidget getPosition Start")
        btn = self.posGroup.checkedButton()
        if debug:  print("easyTextAlongPathWidget getPosition Ende")
        return btn.text()
       
    def __UI_Attr_Distance__(self):
        hbox = QtGui.QHBoxLayout()
        self.Distance = QtGui.QLineEdit()
        self.Distance.setValidator(QtGui.QDoubleValidator())
        self.Distance.setText(str(float(self.obj.Distance)))
        self.Distance.setToolTip(self.obj.getDocumentationOfProperty("Distance"))
        self.Distance.textChanged.connect(self.showPreview)
        hbox.addWidget(self.Distance)
        group = QtGui.QGroupBox("Distance:")
        group.setLayout(hbox)
        hbox = QtGui.QHBoxLayout()        
        hbox.addWidget(group)
        return hbox         
        
    def __UI_Attr_Preview__(self):
        debug = False
        if debug:  print("easyTextAlongPathWidget getPosition Start")
        hbox = QtGui.QHBoxLayout()
        chk = QtGui.QCheckBox("show Preview")
        chk.setChecked(False)
        chk.clicked.connect(self.onPreviewChanged)
        hbox.addWidget(chk)  
        group = QtGui.QGroupBox("Preview:")
        group.setLayout(hbox)
        hbox = QtGui.QHBoxLayout()        
        hbox.addWidget(group)
        return hbox         
        
    def onPreviewChanged(self):
        debug = False
        if debug:  print("easyTextAlongPathWidget onPreviewChanged Start")
        if debug:  print("state: " + str(self.sender().checkState()))
        if debug:  print("self.preview: " + str(self.preview))
        self.preview = self.sender().checkState()        
        if debug:  print("self.preview: " + str(self.preview))
        self.showPreview()
        if debug:  print("easyTextAlongPathWidget onPreviewChanged Ende")
        
    def showPreview(self):
        debug = True        
        if debug:  print("easyTextAlongPathWidget showPreview Start")
        if debug:  print("self.preview: " + str(self.preview))
        self.obj.ViewObject.hide()
        try:
            FreeCAD.ActiveDocument.removeObject("etPreviewTaP")
        except:
            pass
        if not self.preview:
            return
        if self.cbText.currentText() == "" or self.cbWire.currentText() == "":
            return
        tObj = FreeCAD.ActiveDocument.getObjectsByLabel(self.cbText.currentText())[0]
        wObj = FreeCAD.ActiveDocument.getObjectsByLabel(self.cbWire.currentText())[0]
        if not wObj or not tObj:
            return
        offset = float(self.Distance.text())
        position = self.getPosition()
        centerAt = self.getCenterAt()
        if debug:  print("tObj: " + str(tObj.Label))    
        if debug:  print("wObj: " + str(wObj.Label))
        if debug:  print("offset: " + str(offset))
        if debug:  print("position: " + str(position))
        if debug:  print("centerAt: " + str(centerAt))
        wire = wObj.Shape
        textshape = tObj.Shape
        descenderList = tObj.DescenderList
        pathShape = etf.makeGlyph2Path(wire, textshape, descenderList, centerAt = centerAt, position = position, offset = offset)
        if pathShape:
            pobj = Part.show(pathShape, "etPreviewTaP")
            etf.setShapeColor(pobj, (0.00,0.00,0.00))
            
        if debug:  print("easyTextAlongPathWidget showPreview Ende")

    #def onClose(self):
    #    debug = True
    #    if debug:  print("easyTextAlongPathWidget onClose Start")
    #    FreeCAD.Gui.updateGui()
    #    try:
    #        FreeCAD.ActiveDocument.removeObject("etPreviewTaP")
    #    except:
    #        pass
    #    if debug:  print("easyTextAlongPathWidget onClose Ende")
        
    
        
class easyTextAlongPathTaskPanel:
    def __init__(self, viewObject):
        debug = False
        if debug: print("easyTextAlongPathTaskPanel         __init__ Start")
        self.viewObject = viewObject
        self.form = easyTextAlongPathWidget(self.viewObject.Object)
        #self.closeEvent = self.onClose()
        if debug: print("easyTextAlongPathTaskPanel __init__ Ende")

    def accept(self):
        debug = True
        if debug: print("easyTextAlongPathTaskPanel accept Start")
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
        #if debug: print("obj.TextObject: " + str(obj.TextObject))
        obj.WireObject = FreeCAD.ActiveDocument.getObjectsByLabel(self.form.cbWire.currentText())[0]
        #if debug: print("obj.WireObject: " + str(obj.WireObject))
        obj.Distance = float(self.form.Distance.text())
        #obj.Position = self.form.Position.currentText()
        obj.Position = self.form.getPosition()
        obj.CenterAt = self.form.getCenterAt()
        #obj.CenterAt = self.form.CenterAt.currentText()
        redrawTextstring(obj)
        #obj.WireObject.ViewObject.hide()
        obj.TextObject.ViewObject.hide()
        document = self.viewObject.Document.Document
        if debug:  print("document.commitTransaction")
        document.commitTransaction()
        document.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        if debug: print("easyTextAlongPathTaskPanel accept Ende")
        return True
        
    def reject(self):
        debug = True
        if debug:  print("easyTextAlongPathTaskPanel reject Start")
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
        if debug:  print("easyTextAlongPathTaskPanel reject Ende")
        return True
        
    #def onClose(self):
    #    debug = True
    #    if debug:  print("easyTextAlongPathWidget onClose Start")
    #    FreeCAD.Gui.updateGui()
    #    try:
    #        FreeCAD.ActiveDocument.removeObject("etPreviewTaP")
    #    except:
    #        pass
    #    if debug:  print("easyTextAlongPathWidget onClose Ende")
   

        
       
def redrawTextstring(obj):
    debug = False
    if debug: print("easyTextAlongPath redrawTextstring Start")
    executeObject(obj)
    if debug: print("obj.Font: " + str(obj.Font))    
    if debug: print("obj.Text: " + str(obj.Text))
    if debug: print("easyTextAlongPath redrawTextstring Ende")
    

    
        
class CommandEasyTextAlongPath():
    """Command for creating easyTextAlongPath"""    
                
    def GetResources(self):
        return {'Pixmap'  : os.path.join(etf.ICONPATH, 'etTextOnPathIcon.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': "easyTextAlongPath",
                'ToolTip' : __doc__ }
      
    def Activated(self):
        debug = True
        if debug:  print("CommandEasyTextAlongPath Activated Start")
        #FreeCADGui.doCommand("import easyText")
        #FreeCADGui.doCommand("easyText.makeEasyTextString()")
        #FreeCAD.ActiveDocument.openTransaction("easyText")
        if debug:  print("document.openTransaction")
        FreeCAD.ActiveDocument.openTransaction("easyText")
        obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "easyTextAlongPath")
        easyTextAlongPathFeature(obj)
        vp = easyTextAlongPathViewProvider(obj.ViewObject)
        FreeCAD.ActiveDocument.recompute()
        vp.startDefaultEditMode(obj.ViewObject)
        if debug:  print("CommandEasyTextAlongPath Activated Ende")


FreeCADGui.addCommand('easyTextAlongPath', CommandEasyTextAlongPath())
