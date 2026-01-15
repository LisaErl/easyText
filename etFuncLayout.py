from PySide import QtCore, QtGui
import FreeCAD, FreeCADGui

import io
import json
import Part

import os
__dir__ = os.path.dirname(__file__)
    
def getIni(inijs):
    with open(inijs) as json_file:
        inijson = json.load(json_file)
    return inijson
    
def transform(json_obj, indent=4):
    def inner_transform(o):
        if isinstance(o, list) or isinstance(o, tuple):
            for v in o:
                if isinstance(v, dict):
                    return [inner_transform(v) for v in o]
                # elif isinstance(v, list): # check note on the bottom
                #     ...
            return "##<{}>##".format(json.dumps(o))
        elif isinstance(o, dict):
            return {k: inner_transform(v) for k, v in o.items()}
        return o

    if isinstance(json_obj, dict):
        transformed = {k: inner_transform(v) for k, v in json_obj.items()}
    elif isinstance(json_obj, list) or isinstance(json_obj, tuple):
        transformed = [inner_transform(v) for v in json_obj]

    transformed_json = json.dumps(transformed, separators=(', ', ': '), indent=indent)
    transformed_json = transformed_json.replace('"##<', "").replace('>##"', "").replace('\\"', "\"")

    return transformed_json
    
def writeIni(ini, inijs):
    j = transform(ini, indent=4)
    f = open(inijs, "w")
    f.write(j)
    f.close()
    
def getKeys(ini, keylist = None):
    if not keylist:
        return list(ini.keys())
    for key in keylist:
        ini = ini[key]
    try:
        return list(ini.keys())
    except:
        return []
        
def getValue(ini, key, keylist):
    for k in keylist:
        ini = ini[k]
    try:
        return ini[key]
    except:
        return None
        
def setValue(ini, value, key, keylist):
    for k in keylist:
        ini = ini[k]
    val = ini[key]
    if isinstance(val, int):
        if isinstance(value, int):
            ini[key] = value
        elif value.isnumeric() == True:
            ini[key] = int(value)
        else:
            FreeCAD.Console.PrintWarning("Entered value not numeric, no processing" + "\n")
    elif isinstance(val, float):
        try:
            value = float(value)
            ini[key] = value
        except:
            pass
    else:
        ini[key] = value
        
def unicodeFromFile(fileName = None):
    if not fileName:
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        dialog.setDefaultSuffix("htm")
        dialog.setDirectory(__dir__)
        dialog.setNameFilter("HTML Files(*.htm)")
        dialog.setViewMode(QtGui.QFileDialog.Detail)
        dialog.setFilter(QtCore.QDir.Files | QtCore.QDir.Hidden | QtCore.QDir.NoSymLinks)
        dialog.setLabelText(QtGui.QFileDialog.DialogLabel.Accept, "Open")
        if dialog.exec():
            fileName = dialog.selectedFiles()[0]
    if fileName:
        with io.open(fileName, mode="r", encoding="utf-8") as f:
            content = f.read()
    return content, fileName
    
def unicodeToFile(string, fileName = None, dirName = None):
    if not fileName:
        dialog = QtGui.QFileDialog()
        #dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        dialog.setDefaultSuffix("htm")        
        dialog.setDirectory(dirName)
        dialog.setNameFilter("HTML Files(*.htm)")
        dialog.setViewMode(QtGui.QFileDialog.Detail)
        dialog.setFilter(QtCore.QDir.Files | QtCore.QDir.Hidden | QtCore.QDir.NoSymLinks)
        dialog.setLabelText(QtGui.QFileDialog.DialogLabel.Accept, "Save")
        if dialog.exec():
            fileName = dialog.selectedFiles()[0]
    if fileName:
        with io.open(fileName, mode="w", encoding="utf-8") as f:
            f.write(string)
    return fileName
    
def stringToFile(string, fileName = None, dirName = None):
    print("Easytext stringToFile Start")
    print("fileName: " + str(fileName))
    if not fileName:
        dialog = QtGui.QFileDialog()
        #dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        dialog.setDefaultSuffix("htm")        
        dialog.setDirectory(dirName)
        dialog.setNameFilter("HTML Files(*.htm)")
        dialog.setViewMode(QtGui.QFileDialog.Detail)
        dialog.setFilter(QtCore.QDir.Files | QtCore.QDir.Hidden | QtCore.QDir.NoSymLinks)
        dialog.setLabelText(QtGui.QFileDialog.DialogLabel.Accept, "Save")
        if dialog.exec():
            fileName = dialog.selectedFiles()[0]
            print("fileName: " + str(fileName))
    if fileName:
        with open(fileName, 'w') as f:
            f.write(string)
    print("Easytext stringToFile Start")
    return fileName
    
def fileToString(fileName = None):
    string = None
    if not fileName:
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        dialog.setDefaultSuffix("htm")
        dialog.setDirectory(__dir__)
        dialog.setNameFilter("HTML Files(*.htm)")
        dialog.setViewMode(QtGui.QFileDialog.Detail)
        dialog.setFilter(QtCore.QDir.Files | QtCore.QDir.Hidden | QtCore.QDir.NoSymLinks)
        dialog.setLabelText(QtGui.QFileDialog.DialogLabel.Accept, "Open")
        if dialog.exec():
            fileName = dialog.selectedFiles()[0]
            print("fileName: " + str(fileName))
    if fileName:
        with open(fileName, 'r') as f:
            string = f.read()
    return string, fileName
    
def printAllAttributes(obj, indent, attributlist = None):
    #print(" " * indent + "obj: " + str(obj))
    if not attributlist:
        attributlist = [attr for attr in obj.__dir__() if not attr.startswith("_")]
    #print(" " * indent + "attrs: " + str(attrs))
    for attr in attributlist:
        try: 
            value = getattr(obj, attr)()
            print(" " * indent + str(attr) + " : " + str(value))
        except:
            print(" " * indent + str(attr) + " : Error")
            pass
            
