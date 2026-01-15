# -*- coding: utf-8 -*-
from PySide import QtCore, QtGui
import os
import FreeCAD, FreeCADGui

__dir__ = os.path.dirname(__file__)

def get_module_path():
    """ Returns the current module path.
    Determines where this file is running from, so works regardless of whether
    the module is installed in the app's module directory or the user's app data folder.
    (The second overrides the first.)
    """
    return os.path.dirname(__file__)


def makeEasyTextString():
    debug = False
    if debug: print("easyText makeEasyTextString Start")
    FreeCAD.ActiveDocument.openTransaction("easyText")
    '''Python command to create shape for a textstring'''
    import easyTextString
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "easyTextString")
    easyTextString.easyTextStringFeature(obj)
    vp = easyTextString.easyTextStringViewProvider(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    vp.setEdit(obj.ViewObject, 1)
    FreeCADGui.ActiveDocument.resetEdit()    
    FreeCAD.ActiveDocument.commitTransaction() #commit transaction
    if debug: print("easyText makeEasyTextString Ende")
    return obj


def makeEasyTextGlyphs():
    debug = False
    if debug: print("easyText makeEasyTextGlyphs Start")
    FreeCAD.ActiveDocument.openTransaction("easyText")
    '''Python command to create shape for a glyphstring'''
    import easyTextGlyphs
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "easyTextGlyphs")
    easyTextGlyphs.easyTextGlyphsFeature(obj)
    vp = easyTextGlyphs.easyTextGlyphsViewProvider(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    vp.setEdit(obj.ViewObject, 1)
    FreeCADGui.ActiveDocument.resetEdit()    
    FreeCAD.ActiveDocument.commitTransaction() #commit transaction
    if debug: print("easyText makeEasyTextGlyphs Ende")
    return obj


def makeEasyTextAlongPath():
    debug = True
    if debug: print("easyText makeEasyTextAlongPath Start")
    FreeCAD.ActiveDocument.openTransaction("easyText")
    '''Python command to to arrange the letters of a text along a path'''
    import easyTextAlongPath
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "easyTextAlongPath")
    easyTextAlongPath.easyTextAlongPathFeature(obj)
    vp = easyTextAlongPath.easyTextAlongPathViewProvider(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    vp.setEdit(obj.ViewObject, 1)
    FreeCADGui.ActiveDocument.resetEdit()    
    FreeCAD.ActiveDocument.commitTransaction() #commit transaction
    if debug: print("easyText makeEasyTextAlongPath Ende")
    return obj
