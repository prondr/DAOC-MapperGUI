# BoundsRender.py: DAoC mapper, zone boundaries renderer
# See http://www.randomly.org/projects/mapper/ for updates and sample output.
# 	$Id: BoundsRender.py,v 1.10 2004/08/11 16:07:36 cyhiggin Exp $	

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

# Settings options:
#   color: RGB color to fill the boundaries with
#   alpha: alpha to use when filling

# Zones known buggy for borders:
#      052: Avalon Isle - fill spill
#      152: Gripklosa Mountains - fill spill
#      184: Cothrom Gorge - gap in center wall-of-world island. Causes
#                       fill to spill.
#      250: Caledonia
#      251: Murdaigean
#      253: Abermenai
#      252: Thidranki - border is one big polygon, algorithm fills the
#                       inside instead of the outside.

import Tiler
import Image, ImageDraw, re
import datParser as ConfigParser

class BoundsRender(Tiler.Tiler):
    RE_bound = re.compile(r"(\d+),\s*(\d+)")
    
    def __init__(self, zone, name):
        Tiler.Tiler.__init__(self, zone, name)
        self.zone = zone
        self.name = name
        
        bounds = zone.datafile('bound.csv')
        self.data = []
        for l in bounds.readlines():
            matches = BoundsRender.RE_bound.findall(l)
            points = []
            for x, y in matches[1:]:
                points.append( (int(x),int(y)) )

            found = 0
            for i in xrange(len(self.data)):
                ptcheck = self.data[i]                
                if ptcheck[-1] == points[0]:
                    ptcheck.extend(points)
                    found = 1
                elif ptcheck[0] == points[-1]:
                    points.extend(ptcheck)
                    self.data[i] = points
                    found = 1
                elif ptcheck[-1] == points[-1]:
                    points.reverse()
                    ptcheck.extend(points)
                    found = 1
                elif ptcheck[0] == points[0]:
                    ptcheck.reverse()
                    ptcheck.extend(points)
                    found = 1

                if found: break

            if not found:
                self.data.append(points)

        bounds.close()

        # do a similar check within the polygon sets for contiguous polys.
        found = 0
        to_del = []
        for j in xrange(len(self.data)):
            if j in to_del:
                continue
            points = self.data[j]
            for i in range(j+1,len(self.data)):
                if i in to_del:
                    continue
                ptcheck = self.data[i]
                if ptcheck[-1] == points[0]:
                    ptcheck.extend(points)
                    to_del.append(j)
                    found = 1
                elif ptcheck[0] == points[-1]:
                    points.extend(ptcheck)
                    to_del.append(i)
                    found = 1
                elif ptcheck[-1] == points[-1]:
                    points.reverse()
                    ptcheck.extend(points)
                    to_del.append(j)
                    found = 1
                elif ptcheck[0] == points[0]:
                    ptcheck.reverse()
                    ptcheck.extend(points)
                    to_del.append(j)
                    found = 1
                if found:
                    break
        to_del.sort()
        to_del.reverse()
        for i in range(0,len(to_del)):
            del self.data[to_del[i]]
            
        
        # Jump through some hoops to get closed polygons we can fill.
        # We extend any non-closed polygons to the edge of the map, then seal
        # them clockwise around the edge (seems to work well)
        for points in self.data:
            if len(points) > 4 and points[0] != points[-1]:
                tx,ty = points[-1]
                x,y = points[0]

                if tx != 0 and tx != 65536 and ty != 0 and ty != 65536:
                    if tx < 32768: xd = tx
                    else: xd = 65536 - tx

                    if ty < 32768: yd = ty
                    else: yd = 65536 - ty

                    if xd < yd:
                        if tx < 32768: points.append( (0, ty) )
                        else: points.append( (65536, ty) )
                    else:
                        if ty < 32768: points.append( (tx, 0) )
                        else: points.append( (tx, 65536) )

                    tx,ty = points[-1]

                if x != 0 and x != 65536 and y != 0 and y != 65536:
                    if x < 32768: xd = x
                    else: xd = 65536 - x

                    if y < 32768: yd = y
                    else: yd = 65536 - y

                    if xd < yd:
                        if x < 32768: points.insert(0, (0, y) )
                        else: points.insert(0, (65536, y) )
                    else:
                        if y < 32768: points.insert(0, (x, 0) )
                        else: points.insert(0, (x, 65536) )

                    x,y = points[0]
                
                while 1:
                    if y == 0 and y == ty and x <= tx: break
                    if y == 65536 and y == ty and x >= tx: break
                    if x == 0 and x == tx and y >= ty: break
                    if x == 65536 and x == tx and y <= ty: break

                    if y == 0 and x < 65536:
                        points.insert(0, (65536, 0) )
                        x = 65536
                    elif x == 65536 and y < 65536:
                        points.insert(0, (65536, 65536) )
                        y = 65536
                    elif y == 65536 and x > 0:
                        points.insert(0, (0, 65536) )
                        x = 0
                    elif x == 0 and y > 0:
                        points.insert(0, (0, 0) )
                        y = 0
                    else:
                        break # eh.

        if zone.greyscale: color = 0
        else: color = (255, 200, 200, 255)

        self.color = zone.getColor(name, 'color', color)
        try:
            self.alpha = zone.settings.getint(name, 'alpha')
        except ConfigParser.NoOptionError:
            self.alpha = 128
        try:
            self.dofill = (zone.settings.getint(name, 'fill') == 1)
        except  ConfigParser.NoOptionError:
            self.dofill = True
            
    def renderTile(self, dest, tile):                
        i = Image.new('L', (tile[2] - tile[0], tile[3] - tile[1]))
        draw = ImageDraw.Draw(i)
        
        for points in self.data:
            pts = []
            for x,y in points:
                pts.append((self.zone.RToIX(x) - tile[0], self.zone.RToIY(y) - tile[1]))
            if self.dofill:
                draw.polygon(pts, outline=self.alpha, fill=self.alpha)
            else:
                draw.line(pts, fill=self.alpha)  
#            self.color = (255,100,255, 255)  # for testing
        dest.paste(self.color, tile, i)
        del draw
        del i

# ChangeLog
# $Log: BoundsRender.py,v $
# Revision 1.10  2004/08/11 16:07:36  cyhiggin
# sync with mapper-base
#
# Revision 1.5  2004/04/16 22:54:45  cyhiggin
# read fill option to look for 0/1 int instead of yes/no string.
#
# Revision 1.4  2004/04/16 21:12:04  cyhiggin
# Added support for fill setting; 'yes' means draw shaded poly for border,
# 'no' means just draw line.
#
# Revision 1.3  2004/03/16 19:31:55  cyhiggin
# Noted known buggy zones in comments.
#
# Revision 1.2  2004/03/16 17:58:23  cyhiggin
# Added extra step to winnow through polygons checking for polygon sets
# that were made contiguous by the addition of later line segments
# (cf. Oceanus Notos).
#
