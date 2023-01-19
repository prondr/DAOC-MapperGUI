# $Id: RiverRender.py,v 1.5 2004/08/11 16:07:36 cyhiggin Exp $
# RiverRender.py: DAoC mapper, river renderer
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

import re, Image, ImageDraw
import datParser as ConfigParser
import Tiler

class RiverRender(Tiler.Tiler):
    """Renderer class for bodies of water

    member data:
       rivers - list of river data tuples
                (height, leftbank+rightbank, (minx, miny, maxx+1, maxy+1), color)
       alpha - use this transparency for rivers (from settings options)
    """
    
    RE_river = re.compile(r"(\d+),(\d+),\d+")

    def __init__(self, zone, name):
        """Initialize RiverRender
        """
        # This actually runs better with smallish tilesizes
        # since we skip a lot of processing..
        Tiler.Tiler.__init__(self, zone, name)

        try: self.alpha = self.zone.settings.getint(name, 'alpha')
        except ConfigParser.NoOptionError: self.alpha = 64

    def preRender(self):
        """Before rendering, assemble river polygons.

        Reads river data from sector data; parses it into polygons for
        drawing.
        """
        self.rivers = []

        sd = self.zone.sector_dat
        for s in sd.sections():
            if s[:5] == 'river':
                try: count = sd.getint(s, 'bankpoints')
                except ConfigParser.NoOptionError, e: count = 0
                except ValueError, e: count = 0

                if not count: continue
                                    
                leftbank = []
                rightbank = []

                minx = maxx = miny = maxy = None

                for i in xrange(count):
                    lb = sd.get(s, 'left%02d' % i)
                    rb = sd.get(s, 'right%02d' % i)
                    match = RiverRender.RE_river.match(lb)
                    x = self.zone.RToIX(int(match.group(1)) * 256)
                    y = self.zone.RToIY(int(match.group(2)) * 256)
                    leftbank.append( (x,y) )

                    if minx is None:
                        minx = maxx = x
                        miny = maxy = y

                    if x < minx: minx = x
                    if y < miny: miny = y
                    if x > maxx: maxx = x
                    if y > maxy: maxy = y
                                        
                    match = RiverRender.RE_river.match(rb)
                    x = self.zone.RToIX(int(match.group(1)) * 256)
                    y = self.zone.RToIY(int(match.group(2)) * 256)
                    rightbank.append( (x,y) )

                    if x < minx: minx = x
                    if y < miny: miny = y
                    if x > maxx: maxx = x
                    if y > maxy: maxy = y                                        

                rightbank.reverse();                
                height = sd.getint(s, 'height')
                self.zone.riverheight.append(height)
                    
                try:
                    color = int(sd.get(s, 'color'))                
                    color = (color % 256, (color / 256) % 256, color / 65536)
                except ConfigParser.NoOptionError, e:
                    color = (0,0,255)
                    
                color = self.zone.getColor(self.name, 'color', color)
                self.rivers.append( (height, leftbank+rightbank, (minx, miny, maxx+1, maxy+1), color) )

        if self.rivers: self.zone.loadHeightmap()

    def renderTile(self, destimage, tile):
        """actually draw the river
        """
        for height, poly, bounds, color in self.rivers:
            if bounds[0] > tile[2] or bounds[1] > tile[3] or bounds[2] < tile[0] or bounds[3] < tile[1]:
                continue

            tilesize = (tile[2] - tile[0], tile[3] - tile[1])
            rivermap = Image.new('L', tilesize)
            riverdraw = ImageDraw.ImageDraw(rivermap)
            
            polygon = []
            for x,y in poly:
                polygon.append( (x-tile[0], y-tile[1]) )

            riverdraw.polygon(polygon, outline=self.alpha, fill=self.alpha)

            bbox = rivermap.getbbox()
            
            if not bbox:
                continue

            heightmap = self.zone.getHeightmapRegion(tile)
            for y in xrange(bbox[1], bbox[3]):
                for x in xrange(bbox[0], bbox[2]):
                    if heightmap.getpixel((x,y)) > height:
                        rivermap.putpixel((x,y), 0)

            destimage.paste(color, tile, rivermap)
            self.zone.riverdone = 1

# Change History:
# 
# $Log: RiverRender.py,v $
# Revision 1.5  2004/08/11 16:07:36  cyhiggin
# sync with mapper-base
#
# Revision 1.3  2004/08/06 21:40:17  cyhiggin
# zone.riverheight is now a list of all riverheights in the zone
#
# Revision 1.2  2004/07/31 22:55:30  cyhiggin
# Started adding proper docstrings.
# Set zone.riverdone flag when done.
# Set zone.riverheight flag after parsing river data.
#

