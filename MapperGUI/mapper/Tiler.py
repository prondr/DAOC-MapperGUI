# $Id: Tiler.py,v 1.5 2004/08/11 16:07:36 cyhiggin Exp $
# Tiler.py: DAoC mapper, base class for renderers that require tiling
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

# 
class Tiler:
    """This base class decomposes the destination region into a number of tiles,
    then calls renderTile() for each.
    """
    def __init__(self, zone, name):
        self.tilesize = zone.tilesize    
        self.name = name
        self.zone = zone

    def preRender(self):
        pass

    def render(self, destimage, region):
        self.preRender()
        for yl in xrange(region[1], region[3], self.tilesize):            
            if yl + self.tilesize > region[3]:
                yh = region[3]
            else:
                yh = yl + self.tilesize

            for xl in xrange(region[0], region[2], self.tilesize):
                self.zone.progress(self.name, (yl + float(yh-yl) * xl / destimage.size[0]) / destimage.size[1])

                if xl + self.tilesize > region[2]:
                    xh = region[2]
                else:
                    xh = xl + self.tilesize
                
                self.renderTile(destimage, (xl,yl,xh,yh))
                
        self.zone.progress(self.name, 1.0)
        self.postRender()

    def renderTile(self, destimage, tile):
        raise NotImplementedError, "renderTile"

    def postRender(self):
        pass

# Change Log
#
# $Log: Tiler.py,v $
# Revision 1.5  2004/08/11 16:07:36  cyhiggin
# sync with mapper-base
#
# Revision 1.2  2004/07/31 23:31:06  cyhiggin
# Added docstring, id tag.
#
