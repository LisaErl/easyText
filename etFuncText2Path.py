from PySide import QtCore, QtGui
import FreeCAD, FreeCADGui

import math

import DraftGeomUtils
import Part
import Draft

import etFunctions as etf
from etFunctions import _err

blue = (0.0, 0.0, 1.0, 0.0)
red = (1.0, 0.0, 0.0, 0.0)

def makeGlyph2Path(wire, glyphCompound, glyphDesc, centerAt = "Top", position = "Above", offset = 0.0, showAlignWires = False):
    
    debug = True
    if debug: print("etFunctions makeGlyph2Path Start")  
    if debug: print("centerAt: " + str(centerAt))
    alignWire = None
    if wire.isClosed():
        if centerAt == "":
            centerAt = "Top"
        if position == "":
            position = "Outside"
    else:
        centerAt = ""
        if position == "":
            position = "Above"
            
    if debug: print("offset: " + str(offset))
    if debug: print("position: " + str(position))
    # offset = Float mit positivem Wert
    # - die Schrift wird mit dem angegebenen Abstand zum Draht angezeigt
    #
    # Bei geschlossenen Drähten:    
    #
    # centerAt = ["Top", "Bottom"] 
    # - die Schrift wird oben ("Top") bzw. unten ("Bottom") angezeigt 
    # - die Schrift wird um den in Y-Richtung höchsten bzw tiefsten Punkt zentriert
    #
    # position = ["Inside", "Outside"] 
    # - die Schrift wird innerhalb ("Inside") bzw. außerhalb ("Outside") des Drahtes angezeigt 
    # 
    #
    # Bei offenen Drähten:
    #
    # position = ["Above", "Below"] 
    # - die Schrift wird oberhalb ("Above") bzw. unterhalb ("Below") des Drahtes angezeigt 
    #
    if offset < 0:
        _err("etFunctions makeGlyph2Path: Offset must not be negative.")
        return None
    
    shapes = glyphCompound.SubShapes
    textLength = glyphCompound.BoundBox.XLength
    
    # der für den Text benötigte Teil des Wires wird ermittelt,
    # passend zu Textlänge, Ausrichtung und Offset 
    alignWire = makeAlignWire(wire, glyphCompound, centerAt, position, offset)   
    if not alignWire:
        return None
    if math.floor(textLength) > math.floor(alignWire.Length):
        etf._err("etFunctions makeGlyph2Path: textLength (" + str(round(textLength,2)) + ") > Length AlignWire (" + str(round(alignWire.Length,2)) + ")")
        return None
    
    lenlist = getGlyphRectLenList(shapes)
    
    alignWires = makeGlyphAlignWires(alignWire, lenlist)

    textCompound = posGlyphs2AlignWires(alignWires, shapes, glyphDesc)
    if debug: print("etFunctions makeGlyph2Path Ende")
    return textCompound

def makeAlignWire(wire, text, centerAt, position, offset):
    debug = False
    if debug: print("etFunctions makeAlignWire Start") 
    if debug: print("centerAt: " + str(centerAt))
    textlength = math.ceil(text.BoundBox.XLength)
    if wire.isClosed():
        offsetWire, position = makeOffsetWireClosed(wire, text, centerAt, position, offset)
    else:
        offsetWire = makeOffsetWireOpen(wire, text, position, offset)
    if not offsetWire:
        return None
    if debug: Part.show(offsetWire, "offsetWire")
    if textlength > offsetWire.Length:
        etf._err("etFunctions makeGlyph2Path: textLength (" + str(textlength) + ") > Length AlignWire (" + str(round(offsetWire.Length,2)) + ")")
        return None
    centerpoint = getCenterPoint(offsetWire, centerAt)
    if debug: Draft.makePoint(centerpoint, color=red, name='centerpoint', point_size=10)
    alignWire = getAlignWire(offsetWire, textlength, centerpoint)
    if debug: print("etFunctions makeAlignWire Ende")
    return alignWire
    
def makeOffsetWireClosed(wire, tshape, centerAt, position, offset):
    # centerAt = "Top", position = "Outside"
    # - kein zusätzlicher Offset notwendig
    # = return position : "Above"
    # centerAt = "Bottom", position = "Outside"
    # - zusätzlicher Offset + Schrifthöhe
    # = return position : "Below"
    
    # centerAt = "Top", position = "Inside"
    # - zusätzlicher Offset - Schrifthöhe
    # = return position : "Below"
    # centerAt = "Bottom", position = "Inside"
    # - kein zusätzlicher Offset
    # = return position : "Above"
    debug = False
    retPosition = None
    if debug: print("etFunctions makeOffsetWireClosed Start")
    if debug: print("centerAt: " + str(centerAt))
    if debug: print("position: " + str(position))
    if debug: print("offset: " + str(offset))
    if centerAt == "Top":
        if position == "Outside":
            xoff = offset
            retPosition = "Above"
        elif position == "Inside":
            xoff = - (tshape.BoundBox.YLength + offset)
            retPosition = "Below"
    elif centerAt == "Bottom":
        if position == "Outside":
            xoff = tshape.BoundBox.YLength + offset
            retPosition = "Below"
        elif position == "Inside":
            xoff = - (tshape.BoundBox.YLength + offset)
            xoff = - offset
            retPosition = "Above"
    else:
        xoff = offset
    if debug: print("xoff: " + str(xoff))
    if debug: print("retPosition: " + str(retPosition))
    if xoff != 0.0:
        offwire = etf.makeOffset2D(wire, xoff, mode = "Skin", join = "Arcs")
        if debug: print("offwire: " + str(offwire))
        #if debug: Part.show(offwire, "offwire")
        if len(offwire.Wires) > 1:
            _err("etFunctions makeOffsetWireClosed: offset for wire not possible")
            return None, None
        if not offwire.isClosed():
            edges = offwire.Edges + [Part.LineSegment(offwire.Vertexes[-1].Point, offwire.Vertexes[0].Point).toShape()]
            edges = Part.__sortEdges__(edges)
            offwire = Part.Wire(edges)   
    else:
        offwire = wire
    if debug: print("offwire: " + str(offwire))
    if debug: print("offwire.Length: " + str(offwire.Length))
    if debug: print("tshape.BoundBox.XLength: " + str(tshape.BoundBox.XLength))
    if tshape.BoundBox.XLength > offwire.Length:
        _err("etFunctions makeOffsetWireClosed: textLength (" + str(round(tshape.BoundBox.XLength,2)) + ") > Length AlignWire (" + str(round(offwire.Length,2)) + ")")
        return None, None
    if debug: print("etFunctions makeOffsetWireClosed Ende")
    return offwire, retPosition
    
def makeOffsetWireOpen(wire, tshape, position, offset):
    debug = False
    if debug: print("etFunctions makeOffsetWireOpen Start")
    if debug: print("position: " + str(position))    
    if position == "Below":
        offset += tshape.BoundBox.YLength
        offset = -1*offset
        if debug: print("offset: " + str(offset))
    if offset != 0.0:
        offwire = etf.makeOffset2D(wire, offset, mode = "Skin", join = "Arcs")
        if offset > 0 and wire.BoundBox.YMax > offwire.BoundBox.YMax:
            offwire = etf.makeOffset2D(wire, -1*offset, mode = "Skin", join = "Arcs")
        if offset < 0 and wire.BoundBox.YMax < offwire.BoundBox.YMax:
            offwire = etf.makeOffset2D(wire, -1*offset, mode = "Skin", join = "Arcs")
    else:
        offwire = wire
    offwire.fixTolerance(1e-2)
    if debug: print("etFunctions makeOffsetWireOpen Ende")
    return offwire
    
def getWirePointAt(wire, length):
    debug = False
    if debug: print("etFunctions getWirePointAt Start") 
    # zu einem Wire wird zu einer Längenangabe der Punkt ermittelt
    # dieser, sowie der Index der entsprechenden Edge werden zurückgegeben
    if length > wire.Length :
        _err("etFunctions getWirePointAt: length (" + str(length) + ") > Length Wire (" + str(round(wire.Length,2)) + ")")
        return None
    edges = Part.__sortEdges__(wire.Edges)
    lx = length
    for i1, edge in enumerate(edges):
        if debug: print("edge.Length: " + str(edge.Length))
        if debug: print("lx: " + str(lx))
        if edge.Length < lx:
            lx -= edge.Length
        else:
            param = edge.getParameterByLength(lx)
            point = edge.valueAt(param)
            if debug: print("point: " + str(point))
            return [i1, point]
        if debug: print("lx: " + str(lx))
    if debug: print("etFunctions getWirePointAt Ende")
    
def getGlyphRectLenList(shapes):
    debug = False
    # get start and Length of Rect per Glyph from glyphShape Boundbox
    if debug: print("etFunctions getGlyphRectLenList Start")
    lenlist = None
    startlens = [[shape.BoundBox.XMin, shape.BoundBox.XLength] for shape in shapes]
    if debug: [print(str(i1) + " - startPos/length:  " + str(round(sl[0], 2)) + "/" + str(round(sl[1], 2))) for i1, sl in enumerate(startlens)]
    lenlist = [startlens[0][1]]
    lastPos = startlens[0][1]
    for startpos,length in startlens[1:]:
        lenlist.append(startpos - lastPos)
        lenlist.append(length)
        lastPos = startpos + length
    if debug: print("etFunctions getGlyphRectLenList Ende")
    return lenlist
    
def makeGlyphAlignWires(wire, lenList):
    debug = False
    if debug: print("etFunctions makeGlyphAlignWires Start")
    if debug: Part.show(wire, "AlignWire")
    points = getAlignWirePoints(wire, lenList)
    if debug: print("points: " + str(points)) 
    if debug: print("len(points): " + str(len(points))) 
    wireList = []
    for i1 in range(0, len(points), 2):
        if debug: print("i1: " + str(i1))
        if debug: print("points[i1]: " + str(points[i1]))
        if debug: print("points[i1+1]: " + str(points[i1+1]))
        edge = Part.LineSegment(points[i1], points[i1+1]).toShape()
        wireList.append(Part.Wire([edge]))
    #if debug: [Part.show(wire, "wire") for wire in wireList]
    if debug: print("etFunctions makeGlyphAlignWires Ende")
    return wireList
    
def getAlignWirePoints(wire, lenList):
    debug = False
    if debug: print("etFunctions getAlignWirePoints Start")
    if debug: print("min([v.Point.x for v in wire.Vertexes]): " + str(min([v.Point.x for v in wire.Vertexes]))) 
    if wire.Vertexes[0].Point.x > min([v.Point.x for v in wire.Vertexes]):
        if debug: print("reversed")
        wire = wire.reversed()
        points = [wire.Vertexes[-1].Point]
    else:
        points = [wire.Vertexes[0].Point]
    if debug: print("points: " + str(points))
    for i1, length in enumerate(lenList):
        points.append(wire.discretize(float(sum(lenList[:i1+1])))[1])
    if debug: print("etFunctions getAlignWirePoints Ende")
    return points
    
def posGlyphs2AlignWires(alignWires, shapes, desclist):
    debug = False
    if debug: print("etFunctions posGlyphs2AlignWires Start")
    compList = []
    yVal = shapes[0].BoundBox.YMin + desclist[0]
    if debug: print("yVal: " + str(yVal))
    for i1, wire in enumerate(alignWires):
        shape = shapes[i1]
        pobj = FreeCAD.Vector(shape.BoundBox.XMin,yVal,0)
        if debug: print("  pobj: " + str(pobj))
        angle = getHorizontalAngle(wire.Edges[0])
        if debug: print("  angle: " + str(angle))
        diff = wire.Vertexes[0].Point - pobj
        etf.newPlacement(shape, diff = diff, rot = FreeCAD.Rotation(FreeCAD.Vector(0,0,0),angle), center = pobj)
        compList.append(shape)
    if debug: print("etFunctions posGlyphs2AlignWires Ende")
    return Part.Compound(compList)
    
def getHorizontalAngle(edge):
    debug = False
    if debug: print("etFunctions getHorizontalAngle Start")
    p1 = edge.Vertexes[0].Point
    p2 = edge.Vertexes[-1].Point
    x1, y1 = p1.x, p1.y
    x2, y2 = p2.x, p2.y
    dx = x2 - x1
    dy = y2 - y1
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad) 
    if debug: print("etFunctions getHorizontalAngle Ende")
    return angle_deg
    
def getCenterPoint(wire, center):
    debug = False
    if debug: print("etFunctions getAlignCenterPoint Start") 
    if debug: Part.show(wire, "wire_getCenterPoint")
    if wire.isClosed():
        # Mittelpunkt festlegen
        p1 = FreeCAD.Vector(wire.BoundBox.XMin, wire.BoundBox.YMax+5, wire.BoundBox.ZMin)
        p2 = FreeCAD.Vector(wire.BoundBox.XMax, wire.BoundBox.YMax+5, wire.BoundBox.ZMin)
        if center == "Bottom":
            p1.y = wire.BoundBox.YMin-5
            p2.y = wire.BoundBox.YMin-5
        centerEdge = Part.LineSegment(p1, p2).toShape()
        dist, plist, info = wire.distToShape(centerEdge)
        if debug: Draft.makePoint(plist[0][0], color=red, name='cp', point_size=10)
        centerpoint = plist[0][0]
    else:
        e1, p1 = getWirePointAt(wire, wire.Length/2)
        centerpoint = p1
    if debug: Draft.makePoint(centerpoint, color=red, name='centerpoint', point_size=10)
    if debug: print("etFunctions getAlignCenterPoint Ende")
    return centerpoint
    
def getAlignWire(wire, textlen, centerpoint):
    debug = False
    if debug: print("etFunctions getAlignWire Start")
    if debug: print("wire.Length: " + str(wire.Length))
    if debug: print("textlen: " + str(textlen))
    if debug: print("textlen/2: " + str(textlen/2))
    if debug: print("centerpoint: " + str(centerpoint))
    if debug: Part.show(wire, "wire_getAlignWire")
    if debug: Draft.makePoint(centerpoint, color=red, name='centerpoint', point_size=10)
    half = math.ceil(textlen/2)
    out = []
    if wire.isClosed():
        # 1. teilen des Drahtes am Mittelpunkt des Textes
        rightWire, leftWire = splitWireAtPoint(wire, centerpoint)
        if debug: Part.show(rightWire, "rightWire")
        if debug: Part.show(leftWire, "leftWire")
        # wenn der rechte Teil für mehr als die halbe Textlänge ausreicht
        if rightWire.Length > half:
            # wenn der rechte Teil für mehr als die halbe Textlänge ausreicht:
            #ermitteln des überflüssigen Anteils
            wasteLen = math.floor(rightWire.Length-half)
            rest, righthalf = splitWireByLength(rightWire, wasteLen)
            if debug: Part.show(rest, "rest")
            if debug: Part.show(righthalf, "righthalf")
            out = righthalf.Edges
            if leftWire.Length < half:
                leftWire = Part.Wire(Part.__sortEdges__(leftWire.Edges + rest.Edges))
                if debug: Part.show(leftWire, "leftWire")
            if debug: print("leftWire: " + str(leftWire))
            lefthalf, rest = splitWireByLength(leftWire, half)
            if debug: Part.show(rest, "rest")
            if debug: Part.show(lefthalf, "lefthalf")
            out += lefthalf.Edges
        else:
            # wenn der rechte Teil nicht für mehr als die halbe Textlänge ausreicht:
            # umgekehrte Vorgehensweise, erst ermitteln der Edges für den linken Teil
            # dann wegschneiden der Edges des nicht benötigten Teils            
            wasteLen = math.floor(wire.Length-textlen)
            # ermitteln linken Teil
            lefthalf, rest  = splitWireByLength(leftWire, half)
            if debug: Part.show(rest, "rest")
            if debug: Part.show(lefthalf, "lefthalf")
            out = lefthalf.Edges
            waste, righthalf = splitWireByLength(rest, wasteLen)
            out += righthalf.Edges
            out += rightWire.Edges
    else:
        if debug: print("wire open")
        # ermitteln des Überstandes 
        wasteLen = math.floor((wire.Length-textlen)/2)
        if debug: print("wasteLen: " + str(wasteLen))
        waste, textarea = splitWireByLength(wire, wasteLen)
        if debug: Part.show(waste, "waste")
        if debug: Part.show(waste, "textarea")
        textarea, waste = splitWireByLength(textarea, textlen)
        if debug: print("textarea.Length: " + str(textarea.Length))
        if debug: print("waste.Length: " + str(waste.Length))
        out = textarea.Edges
    alignWire = Part.Wire(Part.__sortEdges__(out))
    if debug: Part.show(alignWire, "alignWire")
    if debug: print("etFunctions getAlignWire Ende")
    return alignWire
    
def splitWireAtPoint(wire, point):
    debug = False
    if debug: print("etFunctions splitWireAtPoint Start") 
    if debug: print("point: " + str(point))
    if debug: Draft.makePoint(point, color=red, name='point', point_size=10)
    if debug: Part.show(wire, "wire")
    left = []
    right = []
    out = []
    rightWire = None
    leftWire = None
    for edge in wire.Edges:
        if debug: print("edge: " + str(edge))
        if DraftGeomUtils.isPtOnEdge(point, edge):
            if debug: print("edge.Length: " + str(edge.Length))
            swire = etf.splitEdgeByPoints(edge, [point])
            out.append(swire.Edges[0])
            rightWire = Part.Wire(Part.__sortEdges__(out))
            out = []
            for se in swire.Edges[1:]:
                out.append(se)
        else:
            out.append(edge)
    if debug: print("out: " + str(out))
    leftWire = Part.Wire(Part.__sortEdges__(out))
    if debug: print("etFunctions splitWireAtPoint Ende")
    return rightWire, leftWire
    
def splitWireByLength(wire, length):
    debug = False
    if debug: print("etFunctions splitWireByLength Start") 
    # zu einem Wire wird zu einer Längenangabe der Punkt ermittelt
    # dieser, sowie der Index der entsprechenden Edge werden zurückgegeben
    if debug: print("wire.Length: " + str(wire.Length))
    if debug: print("length: " + str(length))
    if length > wire.Length :
        _err("etFunctions splitWireByLength: length (" + str(length) + ") > Length Wire (" + str(round(wire.Length,2)) + ")")
        return None, None
    edges = Part.__sortEdges__(wire.Edges)
    rightWire = None
    leftWire = None
    lx = length
    out = []
    bout = False
    for i1, edge in enumerate(edges):
        if debug: print("edge.Length: " + str(edge.Length))
        if debug: print("lx: " + str(lx))
        if bout:
            out.append(edge)
        else:
            if edge.Length < lx:
                out.append(edge)
                lx -= edge.Length
            else:
                param = edge.getParameterByLength(lx)
                point = edge.valueAt(param)
                swire = etf.splitEdgeByPoints(edge, [point])
                out.append(swire.Edges[0])
                rightWire = Part.Wire(Part.__sortEdges__(out))
                bout = True
                out = []
                for se in swire.Edges[1:]:
                    out.append(se)
    leftWire = Part.Wire(Part.__sortEdges__(out))
    if debug: print("etFunctions splitWireByLength Ende")
    return rightWire, leftWire
    

