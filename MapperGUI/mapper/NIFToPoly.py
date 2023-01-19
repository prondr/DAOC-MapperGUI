#!/usr/bin/env python

# 	$Id: NIFToPoly.py,v 1.12 2004/08/11 16:07:36 cyhiggin Exp $	

# NIFToPoly.py: Dark Age of Camelot .nif -> polylist convertor.
# See http://www.randomly.org/projects/mapper/ for updates and sample output.

# Copyright (c) 2002, Oliver Jowett <oliver@randomly.org>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of the author may not be used to endorse or promote products
#    derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Updated: 2002/02/09

# This module can be imported or run directly.

# Try:
#   (extract a .npk to a .nif)
#   NIFToPoly.py -poly /some/path/to/model.nif  (writes polylist to model.poly)
#   NIFToPoly.py -text /some/path/to/model.nif  (writes polylist to model.poly.txt)
#   NIFToPoly.py -draw /some/path/to/model.nif  (writes image to model.png)
#   NIFToPoly.py -shade /some/path/to/model.nif (writes flat-shaded image to model-shaded.png)
#   NIFToPoly.py -dump /some/path/to/model.nif  (writes scenegraph dump to model.dump.txt)

# Exporting .nif polygons to a more common modelling format:
#   NIFToPoly.py -dxf /some/path/to/model.nif   (writes polylist to model.dxf)
#   NIFToPoly.py -obj /some/path/to/model.nif   (writes polylist to model.obj)
#   NIFToPoly.py -pov /some/path/to/model.nif   (writes polylist to model.pov)

import struct, os, sys, re
import Util

class error(Exception): pass

#degre de detail lors de l'execution
verbose = 0
traite = 1

def read1(data, i):
    (val,) = struct.unpack('<B',data[i:i+1])
    return i+1, val

def read4(data, i):
    (val,) = struct.unpack('<I', data[i:i+4])
    return i+4, val

def read2(data, i):
    (val,) = struct.unpack('<H', data[i:i+2])
    return i+2, val

def readf(data, i):
    (val,) = struct.unpack('<f', data[i:i+4])
    return i+4, val

def dump(id, nodemap, to, offset=''):
    if verbose > 2: print >>sys.stderr, "demande id %08x" % id 
    if not nodemap.has_key(id): return
    if verbose > 2: print >>sys.stderr, "traite id %08x" % id
    node = nodemap[id]
    node.describe(to, offset)
    for c in node.children:
        dump(c, nodemap, to, offset+'   ')

# Mm. Numeric python would be nice but I don't want to introduce another
# dependency just for some matrix multiplies.
null_xform = ( (1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,1) )

def matrix_multiply(A, B):
    out = []
    for i in xrange(4):
        col = []
        for j in xrange(4):
            col.append( A[0][j] * B[i][0] +
                        A[1][j] * B[i][1] +
                        A[2][j] * B[i][2] +
                        A[3][j] * B[i][3] )
        out.append(tuple(col))        
    return tuple(out)

def transform(A, polylist):
    outlist = []
    for poly in polylist:
        outpoly = []
        for x,y,z in poly:
            newX = A[0][0] * x + A[1][0] * y + A[2][0] * z + A[3][0]
            newY = A[0][1] * x + A[1][1] * y + A[2][1] * z + A[3][1]
            newZ = A[0][2] * x + A[1][2] * y + A[2][2] * z + A[3][2]
            newD = A[0][3] * x + A[1][3] * y + A[2][3] * z + A[3][3]
            outpoly.append( (newX/newD, newY/newD, newZ/newD) )
        outlist.append(tuple(outpoly))
        
    return outlist

class Node:
    def describe(self, to, offset):
        print >>to, offset + '%08x: %s "%s"' % (self.id, self.__class__.__name__, self.name)
        print >>to, offset + "-Attrs:", ",".join(map(lambda x: "%08x" % x, self.attrs))
        print >>to, offset + "-Children:", ",".join(map(lambda x: "%08x" % x, self.children))
        print >>to, offset + "-XForm: ",
        for i in xrange(4):
            if i > 0: print >>to, offset + "        ",
            print >>to, "%5.2f %5.2f %5.2f %5.2f" % (self.local_xform[0][i],
                                                     self.local_xform[1][i],
                                                     self.local_xform[2][i],
                                                     self.local_xform[3][i])

    def polyLocal(self):
        return ()

    def isActive(self):
        return 1

    def isActiveChild(self, id):
        return 1
        
    def polydxf(self, nodemap, xform, outfile, nomobj):
        if not self.isActive(): return ()
        # Apply transform.
        new_xform = matrix_multiply(xform, self.local_xform)
        polylist = transform(new_xform, self.polyLocal())
        nomobj = nomobj + self.name
        if polylist != ():
          for p in polylist:
           count = 0
           print >>outfile, "0"
           print >>outfile, "3DFACE"
           print >>outfile, "8"
           #compatible format
           print >>outfile, "OBJ%08x" % self.id
           #autocad2000 support long name if you do  tr ":" "_"
           #print >>outfile, nomobj
           for x,y,z in p:
              print >>outfile, 10+count
              print >>outfile, x
              print >>outfile, 20+count
              print >>outfile, y
              print >>outfile, 30+count
              print >>outfile, z
              count = count + 1
           print >>outfile, 10+count
           print >>outfile, x
           print >>outfile, 20+count
           print >>outfile, y
           print >>outfile, 30+count
           print >>outfile, z
        # Generate children.
        for c in self.children:
            if nodemap.has_key(c) and self.isActiveChild(c):
                nodemap[c].polydxf(nodemap, new_xform, outfile, nomobj)
        return 

    def poly(self, nodemap, xform):
        if not self.isActive(): return ()

        # Apply transform.
        new_xform = matrix_multiply(xform, self.local_xform)
        polylist = transform(new_xform, self.polyLocal())
        # Generate children.
        for c in self.children:
            if nodemap.has_key(c) and self.isActiveChild(c):
                polylist.extend(nodemap[c].poly(nodemap, new_xform))
        return polylist

class NiNode(Node):
    def read(self, data, offset, format):
        # Name
        offset, l = read4(data, offset)
        self.name = data[offset:offset+l].lower()
        offset += l
        offset += 10
        # transform matrix (or so it appears)
        adjust = []
        for i in xrange(16):
            offset, val = readf(data, offset)
            adjust.append(val)
            if verbose > 3: print >>sys.stderr, "valeur %5.2f" % val
        self.local_xform = (
            (adjust[3], adjust[6], adjust[9], adjust[15]),
            (adjust[4], adjust[7], adjust[10], adjust[14]),
            (adjust[5], adjust[8], adjust[11], adjust[13]),
            (adjust[0], adjust[1], adjust[2], adjust[12]) )
        
        # attr list?
        offset, l = read4(data, offset)
        self.attrs = []
        if verbose > 1: print >>sys.stderr, " nb data a lire (%08x) offset (%08x)" % (l , offset)
        for i in xrange(l):
           if verbose > 1: print >>sys.stderr, "offset (%08x)" % offset
           offset, id = read4(data, offset)
           if verbose > 1: print >>sys.stderr, "inode attr %08x" % id
           self.attrs.append(id)
        # ??? list
        if format == 3: offset, l = read4(data, offset)
        if (format == 41) or (format == 42): offset, l = read1(data,offset)
        if l != 0: print >>sys.stderr, "NiNode list2 not empty at %ld" % (offset-4)

        # child list
        offset, l = read4(data, offset)
        if verbose > 1: print >>sys.stderr, "nb data a lire child (%08x) offset (%08x)" % (l, offset)
        self.children = []
        for i in xrange(l):
          offset, id = read4(data, offset)
          if verbose > 1: print >>sys.stderr, "inode child %08x" % id
          self.children.append(id)
        # ??? list
        offset, l = read4(data, offset)
        if l != 0: print >>sys.stderr, "NiNode list4 not empty at %ld" % (offset-4)

        return offset

    def isActive(self):
        # skip some non-visible nodes
        # it might be nice to draw climb zones somehow..
        if len(self.name) >= 8 and self.name[:8] == 'collidee':
            #elsewhere nrelickeep-s.nif are empty 
            return 0
        if len(self.name) >= 8 and self.name[:8] == 'bounding':
            return 0
        if len(self.name) >= 5 and self.name[:5] == 'climb':
            return 0
        #for nrelickkeep set collidee and unset visible    
        if len(self.name) >= 7 and self.name[:7] == 'visible':
            return 01
        return 1

# just do this for the name
class NiBillboardNode(NiNode): pass

#avoid variable name like Nixxxxxx
class NiStringExtraData(NiNode): 
    def read(self,data,offset,format):
        offset += 4
        offset,l = read4(data,offset)
        offset,m = read4(data,offset)
        self.name=data[offset:offset+m]
        offset +=l-4
        return offset

    def isActive(self):
       return 0   
       
# Level-Of-Detail
class NiLODNode(NiNode):
    def read(self, data, offset, format):
        offset = NiNode.read(self, data, offset, format)
        offset += 8

        # Hm. I can't find a consistent way of interpreting these
        # range numbers; first-child, last-child,
        # child-with-min-range, child-with-max-range all fail on
        # some nifs. So I draw them all :)
        
        #self.bestchild = None
        #bestrange = None
        self.ranges = []
        for i in xrange(len(self.children)):
            offset, val = readf(data, offset)
            self.ranges.append(val)
            #if not self.bestchild or val > bestrange: self.bestchild = self.children[i]
        return offset

    def isActiveChild(self, id):
        return 1
        #return id == self.children[0]
        #return id == self.bestchild

    def describe(self, out, offset):
        NiNode.describe(self, out, offset)
        print >>out, offset + "-Ranges:",
        for r in self.ranges:
            print >>out, "%.2f" % r,
        print >>out

# TriShape contains a TriShapeData
class NiTriShape(Node):
    def read(self, data, offset, format):
        # Name
        offset, l = read4(data, offset)
        self.name = data[offset:offset+l].lower()
        offset += l

        offset += 10

        # Transformation matrix
        adjust = []
        for i in xrange(16):
            offset, val = readf(data, offset)
            adjust.append(val)
            if verbose > 2: print >>sys.stderr, "valeur %5.2f" % val

        self.local_xform = (
            (adjust[3], adjust[6], adjust[9], adjust[15]),
            (adjust[4], adjust[7], adjust[10], adjust[14]),
            (adjust[5], adjust[8], adjust[11], adjust[13]),
            (adjust[0], adjust[1], adjust[2], adjust[12]) )
        
        
        # attr list?
        offset, l = read4(data, offset)
        self.attrs = []
        for i in xrange(l):
            offset, id = read4(data, offset)
            self.attrs.append(id)

        # ??? list
        if format == 3: offset, l = read4(data, offset)
        if (format == 41) or (format == 42): offset, l =read1(data, offset)
        if l != 0: print >>sys.stderr, "NiTriShape list2 not empty at %ld" % (offset-4)

        # Mesh data node
        offset, id = read4(data, offset)
        self.children = [id]

        return offset

colcount = 0

# Mesh data. I ignore a lot of data here, hope it doesn't hurt :)
class NiTriShapeData(Node):
    def read(self, data, offset, format):
        self.name = ''
        self.children = []
        self.attrs = []
        self.points = []
        self.edges = []
        self.local_xform = null_xform

        # point count
        offset, count = read2(data, offset)
        if format == 3: offset += 4
        if (format == 41) or (format == 42): offset += 1
        if verbose > 2: print >>sys.stderr, "nombre de point (%04x)" % count
        # point data
        for i in xrange(count):
            offset, x = readf(data, offset)
            offset, y = readf(data, offset)
            offset, z = readf(data, offset)
            self.points.append((x,y,z))
            if verbose > 3: print >>sys.stderr, i+1, (x,y,z)
        
        # optional? extra data
        if format == 3: offset, val = read4(data, offset)
        if (format == 41) or (format == 42): offset, val = read1(data, offset)
        if val != 0:
            offset += 4 * (count * 3 + 4)
        #driedwell.nif    
        else : offset += 4*4    
        if format == 3: offset, val = read4(data, offset)
        if (format == 41) or (format == 42): offset, val = read1(data, offset)
        if val != 0:
            offset += 4 * count * 4
        offset, multiple = read2(data, offset)
        if format == 3: offset, val = read4(data, offset)
        #if (format == 41) or (format == 42): offset, val = read1(data, offset)
        if (format == 41) or (format == 42): val = multiple
        if val != 0:
            offset += 4 * count * multiple * 2

        # two counts; I have no idea what the first is
        # second is size of edge data to follow
        offset, count = read2(data, offset)
        #if format == 41: offset +=2
        if format == 42: offset -=0
        offset, count = read2(data, offset)
        if format == 3: offset += 2
        if format == 41: offset += 2
        if format == 42: offset += 2
        if verbose > 2: print >>sys.stderr, "nombre triangle (%08x) offset (%08x)" % (count, offset-2)

        # list of three-tuples that describe triangles
        if format == 3:
         for j in xrange(count*2/6):
             offset, p1 = read2(data, offset)
             offset, p2 = read2(data, offset)
             offset, p3 = read2(data, offset)
             if verbose > 3: print >>sys.stderr, " %d %d %d %d" % (j+1, p1, p2, p3)
             self.edges.append((p1,p2,p3))
        else:
         for j in xrange((count+1)*2/6):
             offset, p1 = read2(data, offset)
             offset, p2 = read2(data, offset)
             offset, p3 = read2(data, offset)
             if verbose > 3: print >>sys.stderr, " %d %d %d %d" % (j+1, p1, p2, p3)
             if (p1 != p2) and (p1 != p3) and (p2 != p3) : self.edges.append((p1,p2,p3))

        return offset - 2

    def polyLocal(self):
        # reconstruct triangles from edges + points
        
        out = []
        for e1, e2, e3 in self.edges:
            p1 = self.points[e1%len(self.points)]
            p2 = self.points[e2%len(self.points)]
            p3 = self.points[e3%len(self.points)]
            out.append( (p1, p2, p3) )
                        
        return out

    def describe(self, out, offset):
        Node.describe(self, out, offset)
        print >>out, offset + "-Points:", len(self.points)
        print >>out, offset + "-Edges:", len(self.edges)

# Mesh data. I ignore a lot of data here, hope it doesn't hurt :)
class NiTriStripsData(Node):
    def read(self, data, offset, format):
        self.name = ''
        self.children = []
        self.attrs = []
        self.points = []
        self.edges = []
        self.local_xform = null_xform

        # point count
        offset, count = read2(data, offset)
        if format == 3: offset += 4
        if (format == 41) or (format == 42): offset += 1
        if verbose > 2: print >>sys.stderr, "nombre de point (%04x) offset (%08x)" % (count, offset)
        # point data
        for i in xrange(count):
            offset, x = readf(data, offset)
            offset, y = readf(data, offset)
            offset, z = readf(data, offset)
            self.points.append((x,y,z))
            if verbose > 2: print >>sys.stderr, i+1, (x,y,z)
        
        # optional? extra data
        if format == 3: 
            offset, val = read4(data, offset)
            if val !=0: offset += 4*(count*3+4)
            offset, val = read4(data, offset)
            if val != 0:  offset += 4 * count * 4
            offset, multiple = read2(data, offset)
            offset, val = read4(data, offset)
            if val != 0:  offset += 4 * count * multiple * 2
        #4.2.1.0
        if  (format == 41) or (format == 42): 
            offset,val = read1(data, offset)
            if val != 0 :   offset += 4 * (count * 3 + 4)
            #stone9.nif 4.1.0.12
            else : offset += 4*4
            offset, val = read1(data, offset)
            if val != 0:  offset += 4 * count * 4
            offset, multiple = read2(data, offset)
            val = multiple
            if val != 0:  offset += 4 * count * multiple * 2
                      
        # two counts; I have no idea what the first is
        # second is size of edge data to follow
        offset, count = read2(data, offset)
        if format == 41: offset +=2
        if format == 42: offset +=2
        offset, count = read2(data, offset)
        if format == 3: offset += 2
        if format == 41: offset += 0
        if format == 42: offset += 0
        if verbose > 2: print >>sys.stderr, "nombre triangle (%08x) offset (%08x)" % (count, offset-2)

        # list of three-tuples that describe triangles
        t = 0
        j = 1
        offset,p1 = read2(data,offset)
        offset,p2 = read2(data,offset)
        while (j<count - 1) : 
           offset,p3 = read2(data,offset)
           if (p1 !=p2) and (p1!=p3) and (p2!=p3) : 
             #~ if verbose > 3: print >>sys.stderr, " %d %d %d %d" % (j*2-1, p1, p2, p3)
              #~ self.edges.append((p1,p2,p3))
             #~ if verbose > 3: print >>sys.stderr, " %d %d %d %d" % (j*2, p2, p1, p3)
              #~ self.edges.append((p2,p1,p3))
             if verbose > 3: print >>sys.stderr, " %d %d %d %d" % (j, p1, p2, p3)
             if t : self.edges.append((p1,p3,p2))
             else : self.edges.append((p1,p2,p3))
            
           elif verbose > 3: print >>sys.stderr, " %d %d %d %d not insert" % (j, p1, p2, p3)
  
           j += 1
           p1 = p2
           p2 = p3
           t = not t  

        return offset-2

    def polyLocal(self):
        # reconstruct triangles from edges + points
        
        out = []
        for e1, e2, e3 in self.edges:
            p1 = self.points[e1%len(self.points)]
            p2 = self.points[e2%len(self.points)]
            p3 = self.points[e3%len(self.points)]
            out.append( (p1, p2, p3) )
                        
        return out

    def describe(self, out, offset):
        Node.describe(self, out, offset)
        print >>out, offset + "-Points:", len(self.points)
        print >>out, offset + "-Edges:", len(self.edges)


# Since I don't have a full parser for each node type (and
# there appears to be no size information in the node header),
# I scan the entire file looking for signatures then read
# the nodes I recognize. Luckily each node has a nodeID and
# nodes are crossreferenced by ID so I can link them up after
# the fact.

re_node = re.compile('\x00\x00\x00Ni')

signatures = (
    ('\x06\x00\x00\x00NiNode', NiNode),
    ('\x0f\x00\x00\x00NiBillboardNode', NiBillboardNode),
    ('\x09\x00\x00\x00NiLODNode', NiLODNode),
    ('\x0a\x00\x00\x00NiTriShape', NiTriShape),
    ('\x0e\x00\x00\x00NiTriShapeData', NiTriShapeData),
    ('\x0f\x00\x00\x00NiTriStripsData',NiTriStripsData),
    ('\x0b\x00\x00\x00NiTriStrips', NiTriShape),
    ('\x11\x00\x00\x00NiStringExtraData',NiStringExtraData)
    )

re_signatures = map(lambda x: (re.compile(x[0]), x[1]), signatures)

def load(data):
    # Check file signature.
    filesig = 'NetImmerse File Format, Version 3.'
    #filesig1 = 'NetImmerse File Format, Version 2.3'
    filesig2 = 'NetImmerse File Format, Version 4.1.'
    filesig3 = 'NetImmerse File Format, Version 4.2.'
    numero = -1
    format = 3  
    if verbose >0 :
      offset = 0
      while (offset < len(filesig)+10) and (data[offset:offset+1] > str('\x1f')) :  offset += 1
      print "%s" % data[:offset] 
      
    check = data[:len(filesig)]
    if check == filesig2[:len(filesig)]: 
       check = data[:len(filesig2)]
       if check == filesig2: format = 41
       if check == filesig3: format = 42
    if (check != filesig ) and ( format == 3 ):
        #check = data[:len(filesig1)]
        #if check != filesig1 :
        raise error, "unsupported file format"
    offset = len (data)
    if verbose > 1 : print >>sys.stderr,  "taille fichier %08x" % offset
    offset = 0
    nodemap = {}
    first = -1
    while offset < len(data):
        match = re_node.search(data[offset:])
        if not match: break
        offset += match.start() - 1
        offset, taille = read4(data, offset)
        nom = data[offset:offset+taille]
        offset -= 4
        numero += 1
        if verbose > 0: print >>sys.stderr, "je trouve %s ordre %08x offset (%08x)" % (nom, numero,offset)
        found = 0
        if traite :
         for pattern, ctor in signatures:
            if pattern == data[offset:offset+len(pattern)]:
                offset += len(pattern)
                newnode = ctor() 
                if format == 3: offset, newnode.id = read4(data, offset)
                if (format == 41) or (format == 42): newnode.id =  numero
                if verbose > 0: print >>sys.stderr, "loading: %s (%08x)" % (newnode.__class__.__name__, newnode.id)
                offset = newnode.read(data, offset, format)
                nodemap[newnode.id] = newnode
                if verbose > 0: print >>sys.stderr, "nom %s" % newnode.name
                if first == -1: first = newnode.id
                found = 1
                break

        if not found: offset += 2
        
    return nodemap, first

# Save a polyfile as text.
def savePolysText(polylist, outfile):
    f = open(outfile, 'w')
    for poly in polylist:
        for x,y,z in poly:
            print >>f, x, y, z
        print >>f
    f.close()

# Save a more compact binary polyfile.
def savePolys(polylist, outfile):
    f = open(outfile, 'wb')
    count = 0
    for poly in polylist:
        if len(poly) == 3:
            count += 1
    #print count        
    try:
   #     f.write(struct.pack('H', count))
         f.write(struct.pack('L',count))    # change to unsigned long
    except struct.error, inst:
        print inst,
        print "count = %d" % count
        raise
    for poly in polylist:
        if len(poly) == 3:
            f.write(struct.pack('fffffffff',
                                poly[0][0], poly[0][1], poly[0][2],
                                poly[1][0], poly[1][1], poly[1][2],
                                poly[2][0], poly[2][1], poly[2][2]))
                
#    f.write(struct.pack('H', len(polylist) - count))
    f.write(struct.pack('L', len(polylist) - count))
    for poly in polylist:
        if len(poly) != 3:
            f.write(struct.pack('H', len(poly)))
            for x,y,z in poly:
                f.write(struct.pack('fff', x, y, z))
                
    f.close()

# Reload a polyfile
def loadPolys(infile):
    f = open(infile, 'rb')
    data = f.read()
    f.close()

#    (poly3count,) = struct.unpack('H', data[:2])
#    offset = 2
    (poly3count,) = struct.unpack('L', data[:4])
    offset = 4    
    polylist = []
    for i in xrange(poly3count):
        ptlist = struct.unpack('fffffffff', data[offset:offset+36])
        polylist.append( (ptlist[0:3], ptlist[3:6], ptlist[6:9]) )
        offset += 36
            
##     (polyNcount,) = struct.unpack('H', data[offset:offset+2])
##     offset += 2
    (polyNcount,) = struct.unpack('L', data[offset:offset+4])
    offset += 4
    for i in xrange(polyNcount):
        (ptcount,) = struct.unpack('H', data[offset:offset+2])
        offset += 2
        ptlist = []
        for j in xrange(ptcount):
            ptlist.append(struct.unpack('fff', data[offset:offset+12]))
            offset += 12

        polylist.append(tuple(ptlist))
            
    return polylist

# Draw a top-down (isometric, ignore Z) image of the model
def drawImage(polylist, outfile):
    import Image, ImageDraw
    
    minx = miny = maxx = maxy = None
    for poly in polylist:
        for x,y,z in poly:
            if minx is None or x < minx: minx = x
            if maxx is None or x > maxx: maxx = x
            if miny is None or y < miny: miny = y
            if maxy is None or y > maxy: maxy = y
            
    spanx = maxx - minx
    spany = maxy - miny
    
    scale = 0.5
    
    image = Image.new('L',
                      ( spanx * scale + 10, spany * scale + 10 ), 0)
    draw = ImageDraw.ImageDraw(image)
    
    for poly in polylist:
        templist = []
        for x,y,z in poly:
            templist.append( ((x - minx) * scale + 5,
                              (maxy - y) * scale + 5) )
        draw.polygon(templist, fill=None, outline=255)

    image.save(outfile)

# Draw a top-down isometric shaded model
def drawShaded(polylist, outfile):
    import Image, ImageDraw
    
    minx = miny = maxx = maxy = None
    for poly in polylist:
        for x,y,z in poly:
            if minx is None or x < minx: minx = x
            if maxx is None or x > maxx: maxx = x
            if miny is None or y < miny: miny = y
            if maxy is None or y > maxy: maxy = y
            
    spanx = maxx - minx
    spany = maxy - miny
    
    light = Util.normalize((-1.0,1.0,-1.0))
    lmin = 0.5
    lmax = 1.0
    scale = 0.5

    image = Image.new('L', (spanx * scale + 10, spany * scale + 10))
    draw = ImageDraw.ImageDraw(image)

    drawlist = []
    for poly in polylist:
        # face normal
        n = Util.normalize(Util.normal(poly[0], poly[1], poly[2]))

        # backface cull
        if n[2] < 0.0: continue

        # shade
        ndotl = light[0] * n[0] + light[1] * n[1] + light[2] * n[2]
        if ndotl > 0.0: ndotl = 0.0
        lighting = lmin - (lmax - lmin) * ndotl

        # convert to image coords and prepare to z-sort
        plist = []
        maxz = poly[0][2]
        for x,y,z in poly:
            plist.append( ((x - minx) * scale + 5,
                           (maxy - y) * scale + 5) )
            if z > maxz: maxz = z

        # remember for later drawing
        drawlist.append( (maxz, lighting, tuple(plist)) )

    # Draw in z order
    drawlist.sort()
    for maxz, lighting, plist in drawlist:
        col = 255 * lighting
        draw.polygon(plist, fill=col, outline=col)

    # Save.
    image.save(outfile)

# DXF and OBJ exporters thanks to Clarence Risher <geniusparr@cs.com>.
# (untested here)

def test(id, nodemap, outfile):
    node = nodemap[id]
    f = open(outfile, 'w')
    print >>f, "0"
    print >>f, "SECTION"
    print >>f, "2"
    print >>f, "ENTITIES"
    node.polydxf(nodemap, null_xform, f, "")
    print >>f, "0"
    print >>f, "ENDSEC"  
    print >>f, "0"   
    print >>f, "EOF"
    print >>f
    f.close()

# Save a polyfile as .dxf
# (autocad format, most other 3d modellers should also handle it)
def savePolysDxf(polylist, outfile):
    f = open(outfile, 'w')
    print >>f, "0"
    print >>f, "SECTION"
    print >>f, "2"
    print >>f, "ENTITIES"
    for poly in polylist:
        count = 0
        print >>f, "0"
        print >>f, "3DFACE"
        print >>f, "8"
        print >>f, "CUBE"
        for x,y,z in poly:
            print >>f, 10+count
            print >>f, x
            print >>f, 20+count
            print >>f, y
            print >>f, 30+count
            print >>f, z
            count = count + 1
        print >>f, 10+count
        print >>f, x
        print >>f, 20+count
        print >>f, y
        print >>f, 30+count
        print >>f, z
    print >>f, "0"
    print >>f, "ENDSEC"  
    print >>f, "0"   
    print >>f, "EOF"
    print >>f
    f.close()

# dxf without header for town rendering
def savePolysDxfShort(polylist, outfile, tail):
    f = open(outfile, 'w')
    for poly in polylist:
        count = 0
        print >>f, "0"
        print >>f, "3DFACE"
        print >>f, "8"
        print >>f, tail
        for x,y,z in poly:
            print >>f, 10+count
            print >>f, x
            print >>f, 20+count
            print >>f, y
            print >>f, 30+count
            print >>f, z
            count = count + 1
        print >>f, 10+count
        print >>f, x
        print >>f, 20+count
        print >>f, y
        print >>f, 30+count
        print >>f, z
    f.close()

# Save a polyfile as .obj
# (wavefront/lightwave model format)
def savePolysObj(polylist, outfile):
    f = open(outfile, 'w')
    for poly in polylist:
        for x,y,z in poly:
            print >>f, "v", x, y, z
        print >>f, "f -3 -2 -1"
        print >>f
    f.close() 

def savePolysPovray(polylist, outfile, basename):
    f = open(outfile, 'w')
    print >>f, "#declare " + basename.upper() + " = mesh {"
    for poly in polylist:
        assert len(poly) == 3
        print >>f, "triangle {"
        print >>f, ','.join(map(lambda x: '<%f,%f,%f>' % x, poly))
        print >>f, "}"
    print >>f, "}"
    f.close()
        
def run(argv):
    mode = 'bin'
    if len(argv) < 2:
        print "Usage: %s [-text | -poly | -dump | -draw | -shade | -dxf | -obj | -povray | -dxfs] file.nif ..." % argv[0]
        return 1
    
    for f in argv[1:]:
        if f == '-text': mode = 'text'
        elif f == '-poly': mode = 'bin'
        elif f == '-dump': mode = 'dump'
        elif f == '-draw': mode = 'draw'
        elif f == '-shade': mode = 'shade'
        elif f == '-dxf': mode = 'dxf'
        elif f == '-dxfs' : mode = 'dxfs'
        elif f == '-obj': mode = 'obj'
        elif f == '-povray': mode = 'povray'
        elif f == '-test': mode = 'test'
        else:
            print >>sys.stderr, "Processing", f, "..."
            if verbose>0 : print "%s" % f
            head, tail = os.path.split(f)
            tail = tail[:-4]
        
            inf = open(f, 'rb')
            data = inf.read()
            inf.close()
            
            print >>sys.stderr, "Loading data ..."
            nodemap, first = load(data)
            
            if not nodemap.has_key(first):
                raise error, "No root node found - urk!"
            elif mode == 'dump':
                outfile = tail + ".dump.txt"
                print "Saving", outfile, "(scenegraph dump)"
                outdump = open(outfile, 'w')
                dump(first, nodemap, outdump)
                outdump.close()
            elif mode =='test':
                outfile = tail +".dxf"
                print "wrinting dxf file ......."
                test(first, nodemap, outfile)
                print "done %s ." % outfile 
            else:
                print "Building polylist ..."
                polylist = nodemap[first].poly(nodemap, null_xform)

                if mode == 'draw':
                    outfile = tail + ".png"
                    print "Saving", outfile, "(image)"    
                    drawImage(polylist, outfile)
                elif mode == 'shade':
                    outfile = tail + "-shaded.png"
                    print "Saving", outfile, "(flat-shaded image)"    
                    drawShaded(polylist, outfile)
                elif mode == 'bin':
                    outfile = tail + ".poly"
                    print "Saving", outfile, "(polys)"
                    savePolys(polylist, outfile)
                elif mode == 'text':
                    outfile = tail + ".poly.txt"
                    print "Saving", outfile, "(polys as text)"
                    savePolysText(polylist, outfile)
                elif mode == 'dxf':
                    outfile = tail + ".dxf"
                    print "Saving", outfile, "(polys as dxf)"
                    savePolysDxf(polylist, outfile)
                elif mode == 'dxfs':
                     outfile = tail + ".dxfs"
                     print "Saving", outfile, "(polys as dxf without header)"
                     savePolysDxfShort(polylist, outfile, tail)    
                elif mode == 'obj':
                    outfile = tail + ".obj"
                    print "Saving", outfile, "(polys as obj)"
                    savePolysObj(polylist, outfile)
                elif mode == 'povray':
                    outfile = tail + ".pov"
                    print "Saving", outfile, "(polys as povray mesh)"
                    savePolysPovray(polylist, outfile, tail)

    return 0

if __name__ == '__main__':
    try:
        rv = run(sys.argv)
    except:
        import traceback
        traceback.print_exc()
        rv = 2

    sys.exit(rv)

# Changelog:
#    22-Jan-2002: beta release
#    23-Jan-2002: sort out binary-vs-text problems for win32
#    24-Jan-2002: fix option typo
#    26-Jan-2002: Restructure a little for integration with mapper.py.
#                 Move loadPolys here from mapper.py.
#    03-Feb-2002: Generate greyscale not RGB images for models
#                 Add flat shading of models (adapted from the new
#                  FixtureRender code)
#                 Roll in DXF/OBJ exporter code
#    09-Feb-2002: Add POVRay mesh exporter
###############################################################################
#    20-Nov-2002: modif de dxf export pour pouvoir lire dans amapi et autocad 2000
#                 et ajout d'une routine pour les villes (-dxfs)
#    3-Aout-2003 ajout d'un sortie dxf recursive pour separer les objets (-test)
#   12-Aout-2003 ajout support des nif 4.1 et 4.2 encore imparfait mais ne plante plus
#    5-Sept-2003 NiTriShapeData fixed et NiTriStripsData give a good Z projection
#    6-Sept-2003 NiTriStripsData fixed
###############################################################################
#    $Log: NIFToPoly.py,v $
#    Revision 1.12  2004/08/11 16:07:36  cyhiggin
#    sync with mapper-base
#
#    Revision 1.4  2004/04/01 21:44:59  cyhiggin
#    Save poly count as unsigned long instead of unsigned short. Large
#    models such as volc_minotaur_fot.nif exceed MAXINT for an unsigned
#    short.
#
#    Revision 1.3  2004/04/01 17:52:25  cyhiggin
#    Merged NIF4 and path adjustments from Calien into mapper codebase
#
#    Revision 1.2  2004/03/14 23:25:51  cyhiggin
#    fixtures settings improperly looking for light-vector instead of
#    light-vect, fixed. More trying to find the right path.
#
