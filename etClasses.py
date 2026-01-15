from PySide import QtCore, QtGui
import FreeCAD, FreeCADGui

import Part

def pathElements2Path(elems):
    subPath = QtGui.QPainterPath()
    for i1, elem in enumerate(elems):
        #print("elem: " + str(elem))
        if elem.isMoveTo(): 
            subPath.moveTo(elem.x, elem.y)
        elif elem.isLineTo():
            subPath.lineTo(elem.x, elem.y)
        elif elem.isCurveTo():
            subPath.cubicTo(elems[i1].x, elems[i1].y, elems[i1+1].x, elems[i1+1].y, elems[i1+2].x, elems[i1+2].y)
    return subPath
    
def splitQPainterPath(path):
    subPathElements = []
    subPaths = []
    for i1 in range(path.elementCount()):
        if path.elementAt(i1).isMoveTo():
            if subPathElements:
                subPaths.append(pathElements2Path(subPathElements))
                subPathElements.clear()
        subPathElements.append(path.elementAt(i1))
    if subPathElements:
        subPaths.append(pathElements2Path(subPathElements)) 
    return subPaths

class etTextPath(QtGui.QPainterPath):
    
    def __init__(self, debug = False, *args):
        if debug: print("etTextPath __init__ Start")
        QtGui.QPainterPath.__init__(self, *args)        
        self.debug = debug
        self.GlyphText = None
        self.subPaths = []
        self.glyphPaths = []
        self.GlyphLength = None
        self.Baseline = None
        self.x = None
        if debug: print("etTextPath __init__ Ende")
        
    def addGlyphText(self, offsetX, offsetY, font, text, simplyfied = False):
        if self.GlyphText: return
        self.GlyphText = text
        oldElementCount = self.elementCount()
        if self.debug: print("oldElementCount: " + str(oldElementCount))
        self.addText(offsetX, offsetY, font, text)    
        if simplyfied:
            pp = self.simplified()
            self.clear()
            self.addPath(pp)
        self.makeSubPaths(oldElementCount)
        self.makeGlyphPaths(font, text, simplyfied)
        self.x = QtGui.QPainterPath()
        self.x.addText(offsetX, offsetY, font, "x")
        self.Baseline = self.x.controlPointRect().bottomLeft().y()
        
    def simplify(self, font):
        pp = self.simplified()
        self.clear()
        self.addPath(pp)
        oldElementCount = self.elementCount()
        self.subPaths = []
        self.makeSubPaths(0)
        self.glyphPaths = []
        self.makeGlyphPaths(font, self.GlyphText)
        
    def translateGlyphText(self, qpointf):
        self.translate(qpointf)
        if not self.GlyphText: return   
        for path in self.subPaths:
            path.translate(qpointf)
        for path in self.glyphPaths:
            path.translate(qpointf)
        self.x.translate(qpointf)
        self.Baseline = self.x.controlPointRect().bottomLeft().y()
        
    def makeGlyphPaths(self, font, text, simplified = False):
        subPaths = self.subPaths
        for i1, letter in enumerate(text):
            if letter != " ":
                path = QtGui.QPainterPath()
                path.addText(0, 0, font, letter)
                if simplified:
                    path = path.simplified()
                numPath = len(splitQPainterPath(path))
                if self.debug: print("- numPath: " + str(numPath))        
                glyphPath = QtGui.QPainterPath()
                for path in subPaths[:numPath]:
                    glyphPath.addPath(path)
                self.glyphPaths.append(glyphPath)
                subPaths = subPaths[numPath:]
        startpoint = self.glyphPaths[0].controlPointRect().x()
        endpoint = self.glyphPaths[-1].controlPointRect().x() + self.glyphPaths[0].controlPointRect().width()
        self.GlyphLength = round(endpoint-startpoint, 2)
        
    def makeSubPaths(self, oldElementCount):
        subPathElements = []
        for i1 in range(oldElementCount, self.elementCount()):
            if self.elementAt(i1).isMoveTo():
                if subPathElements:
                    self.subPaths.append(pathElements2Path(subPathElements))
                    subPathElements.clear()
            subPathElements.append(self.elementAt(i1))
        if subPathElements:
            self.subPaths.append(pathElements2Path(subPathElements)) 
        
    def getGlyphRects(self):
        glyphRects = [path.controlPointRect() for path in self.glyphPaths]
        return glyphRects
        
