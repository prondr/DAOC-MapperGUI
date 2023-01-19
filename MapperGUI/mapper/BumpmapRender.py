# BumpmapRender.py: DAoC mapper, bumpmapping using terrain heightfield
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

# Settings options:
#   z_scale: exaggeration factor to apply to heightfield
#   light_vector: x,y,z vector of light (-z is into screen)
#   light_min: color multiplier for "completely dark" pixels
#   light_max: color multiplier for "completely light" pixels

import Tiler, Util
import Image, ImageChops, math
import datParser as ConfigParser

# As inspired by Odin's Eye.
# (I rewrote the actual bumpmapping though, so it made sense ;)

class BumpmapRender(Tiler.Tiler):
    def __init__(self, zone, name):
        Tiler.Tiler.__init__(self, zone, name)

        try: self.z_scale = float(zone.settings.get(name, 'z_scale'))
        except ConfigParser.NoOptionError: self.z_scale = 2.0

        try:
            s = zone.settings.get(name, 'light_vector')
            lv = map(float, s.split(','))
        except ConfigParser.NoOptionError: lv = (-1.0,1.0,-1.0)
        self.lightvect = Util.normalize(lv)

        try: lmin = float(zone.settings.get(name, 'light_min'))
        except ConfigParser.NoOptionError: lmin = 0.6
        try: lmax = float(zone.settings.get(name, 'light_max'))
        except ConfigParser.NoOptionError: lmax = 1.2

        self.lmax = lmax

        lmin_scaled = lmin / lmax
        base = 256 * lmin_scaled
        self.lbase = base + (256 - base)/2
        self.lscale = 256 - self.lbase

    def preRender(self):
        self.zone.loadHeightmap()
        
        # Precalculate lightmap:

        # z-component of surface normals
        nz = 512 / self.z_scale
        nz_2 = nz * nz
        nzlz = nz * self.lightvect[2]

        # create the lightmap for later use
        heightmap = self.zone.heightmap
        lightmap = Image.new('L', (256,256), 0)
        for y in xrange(256):
            self.zone.progress('Generating lightmap', y/256.0)
            if y == 0: y1 = 0
            else: y1 = y-1
            if y == 255: y2 = 255
            else: y2 = y+1                
            
            for x in xrange(256):
                if x == 0: x1 = 0
                else: x1 = x-1
                if x == 255: x2 = 255
                else: x2 = x+1
        
                # compute surface normal
                l = heightmap.getpixel( (x1, y) )
                r = heightmap.getpixel( (x2, y) )
                u = heightmap.getpixel( (x, y1) )
                d = heightmap.getpixel( (x, y2) )
                
                nx = l - r
                ny = u - d
                m_normal = math.sqrt(nx * nx + ny * ny + nz_2)

                # cos(theta) = n.l, simple flat shading
                ndotl = (nx * self.lightvect[0] + ny * self.lightvect[1] + nzlz) / m_normal
                lightmap.putpixel( (x,y), self.lbase - ndotl * self.lscale)
        self.lightmap = lightmap

    def renderTile(self, destimage, tile):
        # Get the right (scaled) portion of the lightmap for this tile.
        light = Util.Scale256(self.zone, self.lightmap, tile)
        if light.mode != destimage.mode:
            light = light.convert(destimage.mode)

        # Darken/brighten the map using the lightmap
        # Unfortunately PIL's ImageChops.multiply only allows you to darken
        # images (<=1.0) so we have to do this in two stages.
        
        new_tile = destimage.crop(tile)
        new_tile = ImageChops.multiply(new_tile, light)
        new_tile = new_tile.point(lambda x,lmax=self.lmax: x*lmax)
        destimage.paste(new_tile, tile)
        del new_tile

    def postRender(self):
        del self.lightmap

