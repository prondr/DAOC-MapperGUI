# $Id: ContourRender.py,v 1.5 2004/08/11 16:07:36 cyhiggin Exp $
# ContourRender.py: DAoC mapper, quick-and-dirty contouring
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


import Zone, Tiler
import datParser as ConfigParser

class ContourRender(Tiler.Tiler):
    """Renderer for contour lines
    
    Settings options:
      interval: height interval between contours (starts at 0)
      steps: number of contour steps to use across the entire zone; overrides
       the value of interval.

    This is horribly slow. You probably don't want to use it for big maps.
    """
    
    def __init__(self, zone, name):
        """Initialize ContourRender

        Uses settings options interval and steps. If not specified,
        interval defaults to 500.
        """
        Tiler.Tiler.__init__(self, zone, name)

        try: self.steps = zone.settings.getint(name, 'steps')
        except ConfigParser.NoOptionError:
            self.steps = None
            try: self.interval = zone.settings.getint(name, 'interval')
            except ConfigParser.NoOptionError: self.interval = 500

    def preRender(self):
        self.zone.loadHeightmap()
        self.minheight, self.maxheight = self.zone.heightmap.getextrema()

    def renderTile(self, destimage, tile):
        """Actually draw the contour lines
        """
        if self.steps:
            range = self.maxheight - self.minheight
            self.interval = range / self.steps
            baselevel = self.minheight
        else:
            baselevel = 0
            range = 8000
        
        # Scale up the terrain map.
        # temp image usage:
        #  1*L(tilesize)
        heightmap = self.zone.getHeightmapRegion((tile[0], tile[1], tile[2]+1, tile[3]+1))

        # This is a bit gross.
        for y in xrange(0, heightmap.size[1]-1):
            next = int((heightmap.getpixel( (0,y) ) - baselevel) / self.interval)
            for x in xrange(0, heightmap.size[0]-1):
                base = next
                next = int((heightmap.getpixel((x+1,y)) - baselevel) / self.interval)
                other = int((heightmap.getpixel((x, y+1)) - baselevel) / self.interval)

                if base != next or base != other:
                    low = base
                    if next < low: low = next
                    if other < low: low = other
                    if self.zone.greyscale: color = int(192.0 * low * self.interval / range)
                    else:
                        c = int(64 + 192.0 * low * self.interval / range)
                        color = (c,c,c)
                    destimage.putpixel((tile[0] + x, tile[1] + y), color)

        del heightmap

# Change Log
#
# $Log: ContourRender.py,v $
# Revision 1.5  2004/08/11 16:07:36  cyhiggin
# sync with mapper-base
#
# Revision 1.2  2004/08/02 04:25:13  cyhiggin
# Started adding proper docstrings
#
