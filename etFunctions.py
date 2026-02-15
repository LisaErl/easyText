from PySide import QtCore, QtGui
import FreeCAD, FreeCADGui

#import io
#import json
import math

import DraftGeomUtils
import Part
import Draft
from enum import Enum

import os
__dir__ = os.path.dirname(__file__)
ICONPATH = os.path.join(__dir__, 'Icons')

from etClasses import etTextPath

userCancelled       = "Cancelled"
userOK          = "OK"

translate = QtCore.QCoreApplication.translate
rot = FreeCAD.Rotation(FreeCAD.Vector(0,0,0),0)
center = FreeCAD.Vector(0,0,0)

blue = (0.0, 0.0, 1.0, 0.0)
red = (1.0, 0.0, 0.0, 0.0)

def makeWire(edges, wires):
    wire = Part.Wire(edges)
    wires.append(wire)
    edges = []
    return edges, wires
            
def makePainterLine(plist):
    edge = Part.LineSegment(plist[0], plist[1]).toShape()
    return edge
    
def makePainterCurve(plist):
    geomCurve = Part.BezierCurve()
    geomCurve.setPoles(plist)
    edge = Part.Edge(geomCurve)
    return edge
            
def makePoint(x, y):
    return FreeCAD.Vector(x, y, 0)
            
def painterPath2Wires(path, setOffset = True):
    debug = False
    if debug: print("etFunctions painterPath2Wires Start")
    if debug: print("path.elementCount(): " + str(path.elementCount()))
    if path.elementCount() == 1:
        return None
    transform = QtGui.QTransform()
    transform.scale(1,-1)
    path = transform.map(path)
    
    if setOffset:
        offset = QtCore.QPointF(0.0,0.0)
        offset.setX(-(path.boundingRect().x() + (path.boundingRect().width()/2)))
        offset.setY(-(path.boundingRect().height()/2))
        path.translate(offset)
    
    if debug: print("path: " + str(path))
    wires = []
    edges = []
    plist = []
    for i1 in range(path.elementCount()):
        if path.elementAt(i1).isMoveTo():
            if plist:
                edges, wires = makeWire(edges, wires)
            plist = [makePoint(path.elementAt(i1).x, path.elementAt(i1).y)]
        elif path.elementAt(i1).isLineTo():
            point = makePoint(path.elementAt(i1).x, path.elementAt(i1).y)
            if point != plist[-1]:
                plist += [point]
                edges.append(makePainterLine(plist))
                plist = [plist[-1]]
        elif path.elementAt(i1).isCurveTo():
            plist += [makePoint(path.elementAt(i1).x, path.elementAt(i1).y)]
            plist += [makePoint(path.elementAt(i1+1).x, path.elementAt(i1+1).y)]
            plist += [makePoint(path.elementAt(i1+2).x, path.elementAt(i1+2).y)]
            edges.append(makePainterCurve(plist))
            plist = [plist[-1]]
            pass
    if plist:
        if debug: print("plist: " + str(plist))
        edges, wires = makeWire(edges, wires)
    if debug: print("wires: " + str(wires))
    wires = [wire for wire in wires if wire.Length > 0.05]
    if debug: print("wires: " + str(wires))
    if debug: print("etFunctions painterPath2Wires Ende")
    return wires    

def isFace1InsideFace2_1(face1, face2):
    pointList = [(v.Point) for v in face1.Vertexes]
    inside = True
    for point in pointList:
        if not face2.isInside(point,0,True):
            inside = False
            break
    return inside
    
def isFace1InsideFace2(face1, face2):    
    pointList = []
    xpos = [v.Point.x for v in face1.Vertexes]
    ypos = [v.Point.y for v in face1.Vertexes]
    for val in [min(xpos), max(xpos), min(ypos), max(ypos)]:
            pointList += [v.Point for v in face1.Vertexes if v.Point.x == val or v.Point.y == val]
    #print("pointList: " + str(pointList))
    inside = True
    for point in pointList:
        if face2.isInside(point,0,True):
            pass
            #print("  - inside")
        else:
            #print("  - outside")
            inside = False
            break
    return inside

def splitEdgeByPoints(edge, pointlist):
    # bei edge.split geht ein vorhandenes Placement verloren
    # dieses wird hier wieder hinzugefügt
    debug = False
    if debug: print("etFunctions splitEdgeByPoints Start")  
    if debug: print("pointlist: " + str(pointlist)) 
    paramlist = []
    for point in pointlist:
        if DraftGeomUtils.isPtOnEdge(point, edge):
            param = edge.Curve.parameter(point)
            if param != 0.0:
                paramlist.append(param)
    if debug: print("paramlist: " + str(paramlist))
    wire = edge.split(paramlist)
    wire.Placement = edge.Placement
    if debug: print("len(wire.Edges): " + str(len(wire.Edges))) 
    if debug: print("etFunctions splitEdgeByPoints Ende")
    return wire
    
def splitEdge(edge, point):
    debug = False
    if debug: print("etFunctions splitEdge Start")  
    if debug: print("point: " + str(point)) 
    ret = None
    for vec in edge.Vertexes:
        if debug: print("vec.Point: " + str(vec.Point))
        if vec.Point == point:
            return [edge]
    param = edge.Curve.parameter(point)
    if debug: print("param: " + str(param))
    if param != 0.0:
        e1, e2 = edge.split(param).Edges
        ret = [e1, e2]
    else:
        ret = [edge]
    if debug: print("etFunctions splitEdge Ende")
    return ret
    
def splitEdgeByLength(edge, length):
    debug = False
    if debug: print("etFunctions splitEdgeByPoints Start")  
    if debug: print("length: " + str(length)) 
    t = edge.getParameterByLength(length)
    wire = edge.split(t)
    wire.Placement = edge.Placement
    if debug: print("len(wire.Edges): " + str(len(wire.Edges))) 
    if debug: print("etFunctions splitEdgeByPoints Ende")
    return wire

def setShapeColor(obj, Color = (0.00,0.00,0.00)):
    obj.ViewObject.ShapeAppearance = FreeCAD.Material(DiffuseColor=Color,AmbientColor=Color,SpecularColor=Color,EmissiveColor=Color,Shininess=(0.90),Transparency=(0.00),)
    obj.ViewObject.LineColor = Color
    obj.ViewObject.PointColor = Color
    
def fontExtToString(qfont):
    debug = False
    if debug: print("etFunctions fontExtToString Start")
    ret = []
    attrs = ["capitalization", "letterSpacing", "wordSpacing", "stretch", "overline"]
    for attr in attrs:
        if debug:print("attr: " + str(attr))
        value = qfont.__getattribute__(attr)()
        if debug:print("value: " + str(value))
        if debug:print("type(value): " + str(type(value)))
        if isinstance(value, bool):  
            if debug:print("bool")
            ret.append(str(int(value)))
        elif isinstance(value, int):
            if debug:print("int")
            ret.append(str(value))
        elif isinstance(value, float):
            if debug:print("float")
            ret.append(str(value))
        elif isinstance(value, Enum):
            if debug:print("Enum")
            ret.append(str(value.value))
        else:
            if debug:print("enum")
            ret.append(str(int(value)))                
    if debug: print("etFunctions fontExtToString Ende")
    return ",".join(ret)
    
def fontExtFromString(qfont, xstr):
    debug = False
    if debug: print("etFunctions fontExtFromString Start")
    extAttr = [QtGui.QFont.Capitalization, "letterSpacing", "wordSpacing", "stretch", "overline"]
    vals = xstr.split(",")
    if debug: print("vals: " + str(vals))
    for i1, key in enumerate(extAttr):
        if key == QtGui.QFont.Capitalization:
            qfont.setCapitalization(key(int(vals[i1])))
        elif key == "letterSpacing":
            qfont.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, float(vals[i1]))
        elif key == "wordSpacing":
            qfont.setWordSpacing(float(vals[i1]))
        elif key == "stretch":
            qfont.setStretch(int(vals[i1]))
        elif key == "overline":
            qfont.setOverline(bool(int(vals[i1])))
    if debug: print("etFunctions fontExtFromString Ende")
    return qfont

def _info(text):
    FreeCAD.Console.PrintNotification(translate("easyText", text) + "\n")
            
def _wrn(text):
    FreeCAD.Console.PrintWarning(translate("easyText", text) + "\n")
    
def _err(text):
    FreeCAD.Console.PrintError(translate("easyText", text) + "\n")
        
def setPointsize(text, font, textHeight, textWidth):
    debug = False
    if debug: print("etFunctions setPointsize Start")
    if debug: print("textHeight: " + str(textHeight))
    if not isinstance(font, QtGui.QFont,):
        qfont = QtGui.QFont()
        qfont.fromString(strFont)
    else:
        qfont = font
    qfont.setPointSize(textHeight)
    path = QtGui.QPainterPath()
    path.addText(0.0, 0.0, qfont, text)
    actHeight = abs(path.boundingRect().height())
    pointsize = math.floor(textHeight/(actHeight/textHeight))
    if textWidth > 0:
        while abs(path.boundingRect().width()) > textWidth:
            qfont.setPointSize(qfont.pointSize()-1)
            path = QtGui.QPainterPath()
            path.addText(0.0, 0.0, qfont, text)
        pointsizeWidth = qfont.pointSize()
        pointsize = min([pointsize, pointsizeWidth])
    qfont.setPointSize(pointsize)
    if debug: print("qfont.pointSize(): " + str(qfont.pointSize()))
    if debug: print("etFunctions setPointsize Ende")
    if isinstance(font, QtGui.QFont,):
        return qfont
    else:
        return qfont.toString()
        
def fixEdge( ed, tol = 0.001):
    # Quelle fixEdge & fixWire: Chris_G - https://forum.freecad.org/viewtopic.php?p=208232&hilit=fixWire#p208232
    if isinstance(ed.Curve,(Part.BezierCurve, Part.BSplineCurve)):
        c = ed.Curve
        fp = c.FirstParameter
        lp = c.LastParameter
        p0 = c.value(fp)
        p1 = c.value(lp)
        straight = True
        degenerated = False
        for p in c.getPoles()[1:-1]:
            if p.distanceToLine(p0,p1.sub(p0)) > tol:
                straight = False
            if (p.distanceToPoint(p0) < tol) or (p.distanceToPoint(p1) < tol):
                degenerated = True
        if straight is True:
            line = Part.LineSegment(p0,p1)
            return(Part.Edge(line))
        elif degenerated is True:
            pts = ed.discretize(100)
            bs = Part.BSplineCurve()
            bs.approximate(Points = pts, DegMin = 2, DegMax = 5, Tolerance = tol)
            bse = bs.toShape()
            return(Part.Edge(bs))
        else:
            return(None)
    else:
        return(None)

def fixWire( wire, tol = 0.001):
    edges = []
    nb = 0
    for e in wire.Edges:
        fe = fixEdge(e, tol)
        if fe is None:
            edges.append(e)
        else:
            nb += 1
            edges.append(fe)
    return Part.Wire(edges)
    
def makeWiresTextString(text, font, fontExt, textHeight = 0, textWidth = 0):
    debug = False
    if debug: print("etFunctions makeWiresTextString Start")
    if debug: print("font: " + str(font))
    if debug: print("fontExt: " + str(fontExt))
    simplified = False
    if not isinstance(font, QtGui.QFont,):
        qfont = QtGui.QFont()
        qfont.fromString(font)
        qfont = fontExtFromString(qfont, fontExt)
    else:
        qfont = font
    if textHeight > 0:
        qfont = setPointsize(text, qfont, int(textHeight), int(textWidth))
    path = QtGui.QPainterPath()
    path.addText(0.0, 0.0, qfont, text)
    wires = painterPath2Wires(path)    
    try:
        [wire.check(True) for wire in wires]
    except:
        path = path.simplified()
        wires = painterPath2Wires(path)
        try:
            [wire.check(True) for wire in wires]
            _wrn("makeWiresTextString: simplified wires for font " + qfont.family())
            simplified = True
        except:
            _err("makeWiresTextString: can't create wires for font " + qfont.family())
    wires = [fixWire(wire) for wire in wires]
    if debug: print("etFunctions makeWiresTextString Ende")
    return wires, qfont.toString(), simplified
    
def makeCutouts(infaces):
    debug = False
    if debug: print("etFunctions makeCutouts Start")
    faces = sortFacesByArea(infaces, reverse = False)
    #if debug: [Part.show(face, "face") for face in faces]
    for i1, face in enumerate(faces):
        if debug: print("i1: " + str(i1))
        for i2, oface in enumerate(faces): 
            if i2 > i1:
                if debug: print("i2: " + str(i2))
                if isFace1InsideFace2(face, oface):
                    if debug: print("  kleineres face in größerem face: cutout")
                    oface = oface.cut(face)
                    oface = shell2face(oface)
                    faces[i1] = None
                    faces[i2] = oface
                    break
    if debug: print("faces: " + str(faces))
    ofaces = [face for face in faces if face]
    if debug: print("ofaces: " + str(ofaces))
    if debug: print("etFunctions makeCutouts Ende")
    return sortFacesByArea(ofaces)
    
def shell2face(inface):
    outface = inface
    if isinstance(inface, Part.Shell):
        if len(inface.childShapes()) == 1:
            if isinstance(inface.childShapes()[0], Part.Face):
                outface = inface.childShapes()[0]
    return outface
    
def makeFacesTextString(text, font, fontExt, textHeight = 0, textWidth = 0, fuse = False):
    debug = False
    if debug: print("etFunctions makeFacesTextString Start")
    wires, font, simplified = makeWiresTextString(text, font, fontExt, textHeight, textWidth)
    if debug: print("fuse: " + str(fuse))
    #if debug:[Part.show(wire, "wire") for wire in wires]
    if debug: print("len(wires): " + str(len(wires)))
    if debug:print("simplified: " + str(simplified))
    #for i1, wire in enumerate(wires):
    #    if wire.isClosed:
    #        pass
    #    else:
    #        print("wire not closed: " + str(i1))
    #    try:
    #        wire.check(True)                        
    #    except:
    #        pass
    sfaces = []
    for i1, wire in enumerate(wires):
        wface = Part.Face(wire)
        try:
            wface.check(True)                        
        except:
            wface.fix(0.1,0,1)
        #wface.check(True)
        sfaces.append(wface)
    # Normalerweise werden die Pfade der Buchstaben nacheinander zurückgegeben, 
    # mehrere Pfade desselben Buchstabens allerdings untereinander in beliebiger Reihenfolge. 
    # Cutouts lieben demnach entweder vor oder hinter dem Bereich, 
    # aus dem sie ausgeschnitten werden müssen.
    # Ein Sonderfall sind Pfade, die durch "simplified" erzeugt werden mussten,
    # beispielsweise weil die ursprünglichen Textpfade ungültig waren.
    # gültig: font = 'Honduro,442,-1,5,50,0,0,0,0,0,Regular'
    # ungültig: font = 'Honduro,442,-1,5,75,0,0,0,0,0,Regular' --> simplified notwendig
    # Nach einem simplified werden die Pfade in unterschiedlicher Reihenfolge und teilweise
    # zusammengefasst zurückgegeben.
    # In diesem Fall ist eine aufwendigere Bearbeitung bei den Cutouts notwendig.
    if simplified:
        #[Part.show(face, "face") for face in sfaces]
        dfaces = makeCutouts(sfaces)
    else:
        dfaces = []
        lastface = None
        for i1, face in enumerate(sfaces):
            if debug: print("i1: " + str(i1))
            if lastface:
                if isFace1InsideFace2(face, lastface):
                    if debug: print("  face in lastface")
                    lastface = lastface.cut(face)
                    lastface = shell2face(lastface)
                    #lastface.sewShape()
                    #lastface = Part.Face(lastface)
                elif isFace1InsideFace2(lastface, face):
                    if debug: print("  lastface in face")
                    lastface = face.cut(lastface)
                    lastface = shell2face(lastface)
                    #lastface.sewShape()
                    #lastface = Part.Face(lastface)
                else:
                    if debug: print("  nichts von beidem")
                    dfaces.append(lastface)
                    lastface = face
            else:
                if debug: print("  lastface setzen")
                lastface = face
        dfaces.append(lastface)
    if fuse:
        dfaces = fuseOverlappingFaces(dfaces)
        #[Part.show(face, "fuse") for face in dfaces]
    if debug: print("etFunctions makeFacesTextString Ende")
    return dfaces, font
    
def makeExtrudesTextGlyphs(text, font, fontExt, extrHeight, textHeight = 0, textWidth = 0, fuse = False):
    debug = False
    if debug:  print("etFunctions makeExtrudesTextGlyphs Start")
    if debug:  print("fuse: " + str(fuse))
    if debug:  print("extrHeight: " + str(extrHeight))
    faces, font, descList = makeFacesTextGlyphs(text, font, fontExt, textHeight, textWidth, fuse)
    extrudes = [face.extrude(FreeCAD.Vector(0,0,extrHeight)) for face in faces]
    if debug:  print("etFunctions makeExtrudesTextGlyphs Ende")
    return extrudes, font, descList
    
def makeExtrudesTextString(text, font, fontExt, extrHeight, textHeight = 0, textWidth = 0, fuse = False):
    faces, font = makeFacesTextString(text, font, fontExt, textHeight, textWidth, fuse)
    #[Part.show(face) for face in faces]
    extrudes = [face.extrude(FreeCAD.Vector(0,0,extrHeight)) for face in faces]
    return extrudes, font

   
def makeTextPixmap(text, font, size):
    print("etFunctions makeTextPixmap Start")
    path = QtGui.QPainterPath()
    path.addText(0, 0, font, text)
    
    transform = QtGui.QTransform()
    transform.translate(50, 50)
    transform.rotate(45)
    transform.scale(0.5, 1.0)
    path = transform.map(path)
    
    pathRect = path.controlPointRect()
    path.translate(4,int(pathRect.height()) + 8)
    #pixmap = QtGui.QPixmap(size)
    pixmap = QtGui.QPixmap(600, 300)
    pixmap.fill(QtCore.Qt.GlobalColor.white)
    painter = QtGui.QPainter(pixmap)
    brush = QtGui.QBrush()
    brush.setColor(QtGui.QColor(QtCore.Qt.black))
    brush.setStyle(QtCore.Qt.SolidPattern)        
    painter.setBrush(brush)
    painter.drawPath(path)
    painter.end()
    print("etFunctions makeTextPixmap Ende")
    return pixmap
    
def newPlacement(obj, diff = FreeCAD.Vector(0,0,0), 
                        rot = FreeCAD.Rotation(FreeCAD.Vector(0,0,0),0), 
                        center = FreeCAD.Vector(0,0,0)):
    obj.Placement = FreeCAD.Placement(diff, rot, center).multiply(obj.Placement)
    #FreeCAD.ActiveDocument.recompute()
    


    
def getEdgeCenter(edge, debug = False):
    debug = False
    if debug: print("etFunctions getEdgeCenter Start")
    t = edge.getParameterByLength(edge.Length/2)
    if debug: print("t: " + str(t))
    v = edge.valueAt(t)
    if debug: print("v: " + str(v))
    if debug: print("etFunctions getEdgeCenter Ende")
    return v
    
def getEdgeDiff(edge, yMin, debug = False):
    if debug: print("etFunctions getEdgeDiff Start")
    if debug: print("yMin: " + str(yMin))
    if debug: Part.show(edge)
    p1 = edge.Vertexes[0].Point - FreeCAD.Vector(0,yMin,0)
    p2 = edge.Vertexes[1].Point - FreeCAD.Vector(0,yMin,0)
    edge1 = Part.LineSegment(p1, p2).toShape()
    if debug: Part.show(edge1)
    if debug: print("edge.Vertexes[0].Point: " + str(edge.Vertexes[0].Point))
    if debug: print("edge1.Vertexes[0].Point: " + str(edge1.Vertexes[0].Point))
    return
    c0 = getEdgeCenter(edge, debug)
    if debug: print("c0: " + str(c0))
    p1 = edge.Vertexes[0].Point
    p2 = edge.Vertexes[0].Point + FreeCAD.Vector(edge.Length,0,0)
    edge1 = Part.LineSegment(p1, p2).toShape()
    if debug: Part.show(edge1)
    c1 = getEdgeCenter(edge1, debug)
    if debug: print("c1: " + str(c1))
    diff = c1 - c0
    if debug: print("diff: " + str(diff))
    if debug: print("etFunctions getEdgeDiff Ende")
    return round(diff.x, 2)
        
def getHorizontalAngle(edge, yMin, debug = False):
    if debug: print("etFunctions getHorizontalAngle Start")
    p1 = edge.Vertexes[0].Point
    p2 = edge.Vertexes[-1].Point
    x1, y1 = p1.x, p1.y
    x2, y2 = p2.x, p2.y
    dx = x2 - x1
    dy = y2 - y1
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad) 
    #getEdgeDiff(edge, yMin, debug)    
    #if debug: print("diffx: " + str(diffx))
    if debug: print("etFunctions getHorizontalAngle Ende")
    return angle_deg, 0
        
def pos2Edge(shape, lastOrg, lastPositioned, edge, yMin = 0, letter = "", debug = False):

    if debug: print("letter: " + str(letter))
    if debug: print("  etFunctions pos2Edge Start")
    dist2Org = 0.0
    dist2Pos = 0.0
    if lastOrg:
        dist2Org, pts, geom = lastOrg.distToShape(shape)
    if debug: print("  yMin: " + str(yMin))    
    pobj = FreeCAD.Vector(shape.BoundBox.XMin,shape.BoundBox.YMin,0)
    angle, diffx = getHorizontalAngle(edge, yMin, False)
    #if debug: print("angle: " + str(angle))
    diff = edge.Vertexes[0].Point - pobj - FreeCAD.Vector(0,yMin,0)
    newPlacement(shape, diff = diff, rot = FreeCAD.Rotation(FreeCAD.Vector(0,0,0),angle), center = pobj)
    if lastPositioned:
        dist2Pos, pts, geom = lastPositioned.distToShape(shape)
    if dist2Pos < dist2Org:
        newPlacement(shape, diff = FreeCAD.Vector(dist2Org-dist2Pos,0,0))
    if debug: print("etFunctions pos2Edge Ende")
    return
    
    
def sortFacesByArea(infaces, reverse = True):
    debug = False
    if debug: print("infaces: " + str(infaces))
    areas = [round(face.Area, 2) for face in infaces]
    areas.sort(reverse=reverse)
    outfaces = []
    for area in areas:
        for i1, face in enumerate(infaces):
            if round(face.Area, 2) == area:
                outfaces.append(face)
                infaces.pop(i1)
    return outfaces
    
def makeQFont(text, font, fontExt, textHeight = 0, textWidth = 0):
    debug = False
    if debug: print("etFunctions makeQFont Start")
    if debug: print("font: " + str(font))
    if debug: print("fontExt: " + str(fontExt))
    if not isinstance(font, QtGui.QFont,):
        qfont = QtGui.QFont()
        qfont.fromString(font)
        qfont = fontExtFromString(qfont, fontExt)
    else:
        qfont = font
    if textHeight > 0:
        qfont = setPointsize(text, qfont, int(textHeight), int(textWidth))
    if debug: print("qfont: " + str(qfont))
    if debug: print("qfont.pointSize(): " + str(qfont.pointSize()))
    if debug: print("etFunctions makeQFont Ende")
    return qfont
    
def getGlyphWires(textPath, qfont):
    debug = False
    if debug: print("etFunctions getGlyphWires Start")  
    #if debug: print("textPath: " + str(textPath))
    wires = painterPath2Wires(textPath)    
    wires = [wire for wire in wires if wire.Length > 0.05]
    if debug: print("wires: " + str(wires))
    #[Part.show(wire, "xwire_" + str(i1)) for i1, wire in enumerate(wires)]
    if debug: print("textPath.glyphPaths: " + str(textPath.glyphPaths))
    textWireList = [painterPath2Wires(glyphPath, False) for glyphPath in textPath.glyphPaths]
    if debug: print("textWireList: " + str(textWireList))
    if debug: print("etFunctions getGlyphWires Ende")
    return textWireList
    
def multiFuse(objList, name, debug = False):
    if debug: print("etFunctions multiFuse Start")                
    if len(objList) == 1:
        obj = objList[0]
        obj.Label = name
        return obj
    multiFuse = FreeCAD.ActiveDocument.addObject("Part::MultiFuse",name)
    multiFuse.Shapes = objList
    if debug: print("etFunctions multiFuse Ende")
    return multiFuse
    
def makeWiresTextGlyphs(text, font, fontExt, textHeight = 0, textWidth = 0):
    debug = False
    if debug: print("etFunctions makeWiresTextGlyphs Start")
    textWireList, font, descList = getTextWireList(text, font, fontExt, textHeight, textWidth)
    shapes = [Part.Compound(glyphWires) for glyphWires in textWireList]
    if debug: print("etFunctions makeWiresTextGlyphs Ende")
    return shapes, font, descList
    

    
def getTextPath(text, qfont):
    debug = False
    if debug: print("etFunctions getTextPath Start")
    if debug: print("qfont: " + str(qfont))
    textPath = etTextPath(False)
    textPath.addGlyphText(0, 0, qfont, text)
    wires = painterPath2Wires(textPath)
    #[Part.show(wire, "owire_" + str(i1)) for i1, wire in enumerate(wires)]
    if debug: print("len(wires): " + str(len(wires)))          
    try:
        [wire.check(True) for wire in wires]
    except:
        textPath = etTextPath(False)
        debug = False
        textPath.addGlyphText(0, 0, qfont, text, simplyfied = True)
        if debug: print("textPath: " + str(textPath))
        wires = painterPath2Wires(textPath)
        if debug: print("wires: " + str(wires))
        #if debug: return wires
        if debug: print("len(wires): " + str(len(wires)))  
        try:
            [wire.check(True) for wire in wires]
            _wrn("getTextPath: simplified wires for font " + qfont.family())
        except:
            _err("getTextPath: can't create wires for font " + qfont.family())
            return None    
    if debug: print("etFunctions getTextPath Ende")
    return textPath
    
def getDescenderList(textPath):
    debug = False
    if debug: print("etFunctions getDescenderList Start")    
    # The descender is calculated for each glyph
    if debug: print("textPath.Baseline: " + str(textPath.Baseline))  
    if debug: print("etFunctions getDescenderList Ende")
    return [rect.bottomLeft().y() - textPath.Baseline for rect in textPath.getGlyphRects()]
    
def getTextWireList(text, font, fontExt, textHeight = 0, textWidth = 0):
    debug = False
    if debug: print("etFunctions getTextWireList Start")
    qfont = makeQFont(text, font, fontExt, textHeight, textWidth)
    if debug: print("qfont: " + str(qfont))    
    if debug: print("qfont.overline(): " + str(qfont.overline()))  
    textPath = getTextPath(text, qfont)
    if textPath:
        textPath.translateGlyphText(QtCore.QPointF(-textPath.controlPointRect().x(),textPath.controlPointRect().height()))
        textLength = textPath.controlPointRect().width()
        textWireList = getGlyphWires(textPath, qfont)
        descList = getDescenderList(textPath)
        if debug: print("descList: " + str(descList))
    else:
        textWireList = None
        descList = []
    if debug: print("etFunctions getTextWireList Ende")
    return textWireList, qfont.toString(), descList
    
    
def makeGlyphFace(wires):
    debug = False
    if debug: print("etFunctions makeGlyphFace Start")
    if debug: print("wires: " + str(wires))
    if debug: print("fuse: " + str(fuse))
    faces = []
    for i1, wire in enumerate(wires):
        wface = Part.Face(wire)
        try:
            wface.check(True)                        
        except:
            wface.fix(0.1,0,1)
        #wface.check(True)
        faces.append(wface)
    if debug: print("faces: " + str(faces))
    shape = None
    cutFace = False
    faces = sortFacesByArea(faces)    
    #if debug: print("faces: " + str(faces))
    for i1, face in enumerate(faces):
        #if debug: Part.show(face, "Face" + str(i1))
        cutFace = False
        if shape:
            #if debug: Part.show(shape, "Shape")
            #if debug: Part.show(face, "Face")
            for i1, sFace in enumerate(shape.Faces):
                if isFace1InsideFace2(face, sFace):
                    cutFace = True
            #if debug: print("cutFace: " + str(cutFace))
            if cutFace:
                shape = shape.cut(face)
            else:
                shape = shape.fuse(face)
                #shape.sewShape()
                shape = shape.removeSplitter()
        else:
            shape = face
    shape = shape.removeSplitter()
    if isinstance(shape, Part.Shell):
        if len(shape.childShapes()) == 1:
            if isinstance(shape.childShapes()[0], Part.Face):
                shape = shape.childShapes()[0]
    #Part.show(shape)
    if debug: print("etFunctions makeGlyphFace Ende")
    return shape
    
def fuseFace(fusion, face):
    debug = False
    if debug: print("etFunctions fuseFace Start")
    if debug: print("fusion vorher: " + str(fusion))
    if debug: print("face vorher: " + str(face))
    if debug:Part.show(fusion, "fusion vorher")
    if debug:Part.show(face, "face vorher")
    fusion = fusion.fuse(face)
    fusion = shell2face(fusion)
    #if fusion:
    #    fusion.sewShape()
    if fusion:
        fusion = fusion.removeSplitter()
    if debug: print("fusion nachher: " + str(fusion))
    fusion = shell2face(fusion)
    if debug: print("fusion nach shell2face: " + str(fusion))
    if debug:Part.show(fusion, "fusion nachher")
    if debug: print("etFunctions fuseFace Ende")
    return fusion
    
def findFace2Fuse(fusion, faces):
    debug = False
    if debug: print("etFunctions findFace2Fuse Start")
    for i1, face in enumerate(faces):
        if fusion:
            dist, pts, info = face.distToShape(fusion)
            if debug:print("dist: " + str(dist))
            if dist == 0.0:
                faces.pop(i1)
                fusion = fuseFace(fusion, face)
                return fusion, faces, True
        else:
            faces.pop(i1)
            fusion = face
            return fusion, faces, True    
    if debug: print("etFunctions findFace2Fuse Ende")
    return fusion, faces, False
    
def fuseOverlappingFaces(shapelist):
    debug = False
    if debug: print("etFunctions fuseOverlappingFaces Start")
    fusion = None
    faces = [face for face in shapelist if isinstance(face, Part.Face,)]    
    for shape in shapelist:
        if isinstance(shape, Part.Compound,):
            faces = faces + shape.SubShapes
    if debug:print("len(faces): " + str(len(faces)))
    i1 = 0
    while True:
        if debug:print("i1: " + str(i1))
        i1 += 1
        fusion, faces, ret = findFace2Fuse(fusion, faces)
        if debug: 
            print(" ret: " + str(ret))
            print(" fusion: " + str(fusion))
            print(" len(faces): " + str(len(faces)))
            if fusion:
                if debug:Part.show(fusion, "fusion_"+str(i1))
            #[Part.show(face, "faces"+str(i1)) for face in faces]
        if ret == False:
            break
    if debug: print("etFunctions fuseOverlappingFaces Ende")
    return [fusion] + faces
    
def makeFacesTextGlyphs(text, font, fontExt, textHeight = 0, textWidth = 0, fuse = False):
    debug = False   
    if debug: print("etFunctions makeFacesTextGlyphs Start")
    if debug: print("font: " + str(font))
    if debug: print("fontExt: " + str(fontExt))
    if debug: print("fuse: " + str(fuse))
    textWireList, font, descList = getTextWireList(text, font, fontExt, textHeight, textWidth)
    if debug: print("textWireList: " + str(textWireList))
    shapes = []
    if textWireList:
        for i1, glyphWires in enumerate(textWireList):            
            if debug: print("glyphWires: " + str(glyphWires))
            if len(glyphWires) > 0:
                shape = makeGlyphFace(glyphWires)
                shapes.append(shape)              
    if fuse:
        shapes = fuseOverlappingFaces(shapes)
    if debug: print("etFunctions makeFacesTextGlyphs Ende")
    return shapes, font, descList
    
def makeOffset2D(wire, offset, mode = "Pipe", join = "Arcs", collectiveOffset = False, fill = False):
    debug = False
    if debug: print("etFunctions makeOffset2D Start")
    ljoin = ["Arcs", "Tangent", "Intersection"]
    lmode = ["Pipe", "Skin"]
    if debug: print("offset: " + str(offset))
    # cut edge to prevent error "makeOffset2D: wires are nonplanar or noncoplanar"
    # which is output when it is a wire with a single straight edge
    if debug: print("len(wire.Edges): " + str(len(wire.Edges)))
    if len(wire.Edges) == 1 and isinstance(wire.Edges[0].Curve, Part.Line,):
        if debug: print("single straight edge")
        point = wire.discretize(3)[1]
        wire = splitEdgeByPoints(wire.Edges[0], [point])
    offshape = wire.makeOffset2D(offset, join = ljoin.index(join), openResult = bool(lmode.index(mode)))
    if debug: print("offshape: " + str(offshape))
    #if debug: Part.show(offshape, "offshape")
    if debug: print("etFunctions makeOffset2D Ende")
    return offshape

def isPtOnWire(point, wire):
    for edge in wire.Edges:
        if DraftGeomUtils.isPtOnEdge(point, edge):
            return True
    return False

def getGlyphObjects():
    debug = False
    if debug: print("easyTextAlongPathWidget getTextObjects Start") 
    options = []
    for obj in FreeCAD.ActiveDocument.Objects:
        if debug: print("obj.Label: " + str(obj.Label))
        if hasattr(obj, "Proxy"):
            if hasattr(obj.Proxy, "Type"):
                if debug: print("obj.Proxy.Type: " + str(obj.Proxy.Type))
                if obj.Proxy.Type == "easyTextGlyphs":
                    options.append(obj.Label)
    if debug: print(options)
    if debug: print("easyTextAlongPathWidget getTextObjects Ende")
    return options
    
def getWireObjects():
    debug = False
    if debug: print("easyTextAlongPathWidget getTextObjects Start") 
    options = []
    for obj in FreeCAD.ActiveDocument.Objects:
        if debug: print("obj.Label: " + str(obj.Label))
        if isinstance(obj, Part.Feature):
            if isinstance(obj.Shape, Part.Wire,):
                options.append(obj.Label)
    if debug: print(options)
    if debug: print("easyTextAlongPathWidget getTextObjects Ende")
    return options
    
def pointOnEdgeByLen(edge, length):
    debug = False
    if debug: print("etFunctions pointOnEdgeByLen Start") 
    t = edge.getParameterByLength(length)
    if debug: print("t: " + str(t))
    v = edge.valueAt(t)
    if debug: print("v: " + str(v))
    if debug: print("etFunctions pointOnEdgeByLen Ende")
    return v

def makeBottom4Shape(shape, height, addX, addY, cornerFilletRadius, topFilletRadius):
    x = math.ceil(shape.BoundBox.XLength) + int(addX)
    y = math.ceil(shape.BoundBox.YLength) + int(addY)
    points = [FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,y,0), FreeCAD.Vector(x,y,0), FreeCAD.Vector(x,0,0)]
    edges = [Part.LineSegment(p1, p2).toShape() for p1, p2 in zip(points,points[1:] + [points[0]])]
    bottom = Part.Face(Part.Wire(edges))
    bottom = bottom.extrude(FreeCAD.Vector(0,0,-height))
    diff = shape.BoundBox.Center - bottom.BoundBox.Center
    diff.z = 0
    newPlacement(bottom, diff = diff)
    if cornerFilletRadius > 0:
        edges = [edge for edge in bottom.Edges if edge.BoundBox.ZMin == bottom.BoundBox.ZMin and edge.BoundBox.ZMax == bottom.BoundBox.ZMax]
        bottom = bottom.makeFillet(cornerFilletRadius, edges)
    if topFilletRadius > 0:
        edges = [edge for edge in bottom.Edges if edge.BoundBox.ZMin == bottom.BoundBox.ZMax and edge.BoundBox.ZMax == bottom.BoundBox.ZMax]
        bottom = bottom.makeFillet(topFilletRadius, edges)    
    return bottom

def makeGlyphRevolve(tobj, degree, forceBaseline, sunken, makeBase, baseHeight, baseAddX, baseAddY, baseCornerFilletRadius, baseTopFilletRadius):
    bottom = None
    descenderList = tobj.DescenderList
    glyphs = tobj.Shape.SubShapes
    if forceBaseline:
        for desc, glyph in zip(descenderList, glyphs):
            if desc > 0.0:
                newPlacement(glyph, diff = FreeCAD.Vector(0,desc,0))
        descenderList = [0.0,] * len(descenderList)
    if max(descenderList) > 0.0:
        _err("etFunctions makeGlyphRevolution: The individual letters do not all lie on the baseline, and therefore a revolution cannot be performed. A common baseline can be forced using the `forceBaseline` parameter.")
        return None
    shape = Part.Compound(glyphs)
    if makeBase:
        bottom = makeBottom4Shape(shape, baseHeight, baseAddX, baseAddY, baseCornerFilletRadius, baseTopFilletRadius)
    revolveBase = FreeCAD.Vector(shape.BoundBox.XMax, shape.BoundBox.YMin, shape.BoundBox.ZMin)
    revolveAxis = FreeCAD.Vector(1,0,0)
    revolveAngle = degree
    rshape = shape.revolve(revolveBase, revolveAxis, revolveAngle)
    newPlacement(rshape, diff = FreeCAD.Vector(0,0,-sunken))
    if bottom:
        rshape = Part.Compound([rshape, bottom])
    return rshape
    







