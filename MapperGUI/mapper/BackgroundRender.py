# BackgroundRender.py: DAoC mapper background image renderer
# See http://www.randomly.org/projects/mapper/ for updates and sample output.
# 	$Id: BackgroundRender.py,v 1.13 2004/08/11 16:07:36 cyhiggin Exp $	

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

# Settings options: none

import os, Image, ImageFilter
import dempak, Tiler, DdsImageFile
import datParser as ConfigParser
import re

# mapping of 'new' background texture files to zones.
texture_map = {
    # zone # : ('filename',dimensions,#tiles_across),
    0   : ('CamHills-Small',1024,1),
    4   : ('dartmoor',1024,1),
    116 : ('Malmohus',1024,1),
    163 : ('oceanfloor',512,8),
    164 : ('oceanfloor',512,8),
    167 : ('Odin_color',1024,1),
    168 : ('Jamtland_color',1024,1),
    169 : ('Yggdra_color',1024,1),
    170 : ('Uppland_color',1024,1),
    171 : ('EmainMacha_color',1024,1),
    172 : ('Breifine_color',1024,1),
    173 : ('CruachanGorge_color',1024,1),
    174 : ('MtCollory_color',1024,1),
    175 : ('Snowdonia_color',1024,1),
    176 : ('Sauvage_color',1024,1),
    177 : ('PennineMts_color',1024,1),
    178 : ('HadriansWall_color',1024,1),
    216 : ('SheeroeHills',1024,1),
    234 : ('zone234_color',1024,1),
    236 : ('zone236_color',1024,1),
    237 : ('zone237_color',1024,1),
    238 : ('zone238_color',1024,1),
    239 : ('zone239_color',1024,1),
    240 : ('zone240_color',1024,1),
    241 : ('zone241_color',1024,1),
    242 : ('zone242_color',1024,1),
    254 : ('zone254_color',1024,1)
    }

class BackgroundRender(Tiler.Tiler):
    def __init__(self, zone, name):
        Tiler.Tiler.__init__(self, zone, name)

        # These are needed for the epic zones.
        try:
            self.zoneID = zone.sector_dat.getint('terrain', 'use_texture')
        except ConfigParser.NoOptionError:
            self.zoneID = zone.zoneID
        else:
            if zone.sector_dat.has_option('terrain','ignore_use_texture'):
                if zone.sector_dat.getint('terrain','ignore_use_texture') == 1:
                    self.zoneID = zone.zoneID
            
        # modified for handling housing zones
        try: 
           tx = zone.sector_dat.get('terrain', 'flip_x')
           print tx
           if  (tx == '1') or (tx =='-1'):
              self.flip_x = True 
           else: 
              self.flip_x = False
        except ConfigParser.NoOptionError: self.flip_x = 0
        
        try: 
          ty = zone.sector_dat.get('terrain', 'flip_y')
          print ty
          if ty == '1' or ty =='-1' :
            self.flip_y = True
          else :
            self.flip_y = False  
        except ConfigParser.NoOptionError: self.flip_y = 0

    # Temporary images:
    #  colour: ~2*RGB(tilesize)
    #  greyscale: ~2*L(tilesize)
    def renderOldTexTile(self, destimage, tile):
        #bmpsize = (self.zone.RToIScale(8192), self.zone.RToIScale(8192))
  
        # decide if we need to use .bmp or .dds images
        try:
            self.texfile.open('tex00-00.dds').close()
            sourcesize = 512
            usedds = 1
        except IOError, e:
            sourcesize = 256
            usedds = 0

        sourcescale = 8192.0 / sourcesize

        # Calculate the "interesting" range of background tiles for this
        # output tile
        if self.flip_x:
            xl = int((65536 - self.zone.IToRX(tile[2]) - 8191) / 8192)
            xh = int((65536 - self.zone.IToRX(tile[0])) / 8192)
        else:
            xl = int(self.zone.IToRX(tile[0]) / 8192)
            xh = int((self.zone.IToRX(tile[2]) + 8191) / 8192)

        if self.flip_y:
            yl = int((65536 - self.zone.IToRY(tile[3]) - 8191) / 8192)
            yh = int((65536 - self.zone.IToRY(tile[1])) / 8192)
        else:
            yl = int(self.zone.IToRY(tile[1]) / 8192)
            yh = int((self.zone.IToRY(tile[3]) + 8191) / 8192)
        
        for y in xrange(yl, yh+1):
            if y < 0 or y > 7: continue
            if self.flip_y: basey = 65556 - (y+1) * 8192
            else: basey = y * 8192
            miny = self.zone.RToIY(basey)
            maxy = self.zone.RToIY(basey + 8192)
            if maxy < tile[1] or miny > tile[3]: continue
            
            for x in xrange(xl, xh+1):
                if x < 0 or x > 7: continue
                if self.flip_x: basex = 65556 - (x+1) * 8192
                else: basex = x * 8192
                minx = self.zone.RToIX(basex)
                maxx = self.zone.RToIX(basex + 8192)
                if maxx < tile[0] or minx > tile[2]: continue

                # Now jump through lots of hoops to avoid resizing the
                # entire source image (that kills us on very large scales,
                # regardless of the actual tile or region size, since at
                # e.g. scale=16384, each background image becomes a
                # 2048x2048 image...)

                # Calculate bounds of tile on this image
                srcbounds = [int((self.zone.IToRX(tile[0]) - basex) / sourcescale + 0.5) - 1,
                             int((self.zone.IToRY(tile[1]) - basey) / sourcescale + 0.5) - 1,
                             int((self.zone.IToRX(tile[2]) - basex) / sourcescale + 0.5) + 1,
                             int((self.zone.IToRY(tile[3]) - basey) / sourcescale + 0.5) + 1]

                # Crop to actual source dimensions
                if srcbounds[0] < 0: srcbounds[0] = 0
                if srcbounds[1] < 0: srcbounds[1] = 0
                if srcbounds[2] > sourcesize: srcbounds[2] = sourcesize
                if srcbounds[3] > sourcesize: srcbounds[3] = sourcesize
                if srcbounds[2] <= srcbounds[0] or srcbounds[3] <= srcbounds[1]: continue # no image on this tile.

                # Determine the projection of this source rectangle onto the destination image.
                destbounds = [self.zone.RToIX(basex + srcbounds[0] * sourcescale),
                              self.zone.RToIY(basey + srcbounds[1] * sourcescale),
                              self.zone.RToIX(basex + srcbounds[2] * sourcescale),
                              self.zone.RToIY(basey + srcbounds[3] * sourcescale)]

                # Determine what to resize the image to.
                resize_to = (destbounds[2] - destbounds[0],destbounds[3] - destbounds[1])

                # Clip destbounds against the actual tile. Remember where the clipping occurs.
                usebounds = [0,0,destbounds[2]-destbounds[0],destbounds[3]-destbounds[1]]
                if destbounds[0] < tile[0]:
                    usebounds[0] += tile[0] - destbounds[0]
                    destbounds[0] = tile[0]                    
                if destbounds[1] < tile[1]:
                    usebounds[1] += tile[1] - destbounds[1]
                    destbounds[1] = tile[1]
                if destbounds[2] > tile[2]:
                    usebounds[2] -= destbounds[2] - tile[2]
                    destbounds[2] = tile[2]
                if destbounds[3] > tile[3]:
                    usebounds[3] -= destbounds[3] - tile[3]
                    destbounds[3] = tile[3]

                #print tile, srcbounds, resize_to, usebounds, destbounds
                
                # Acquire and crop/resize/etc image
                if usedds: i = Image.open(self.texfile.open('tex%02d-%02d.dds' % (x, y)))
                else: i = Image.open(self.texfile.open('tex%02d-%02d.bmp' % (x, y)))

                if self.flip_x: i = i.transpose(Image.FLIP_LEFT_RIGHT)
                if self.flip_y: i = i.transpose(Image.FLIP_TOP_BOTTOM)
                if self.zone.greyscale: i = i.convert('L')
                else: i = i.convert('RGB')

                i = i.crop(srcbounds)
                i = i.resize(resize_to, Image.BILINEAR)
                i = i.crop(usebounds)

                # Paste tile.
                destimage.paste(i, destbounds)

    COLORTEXRE = re.compile(r',([a-zA-Z0-9]+_color),', re.I)
    
    def renderNewTerTile(self, destimage, tile):
        usedds = 1
        sourcesize = 1024
        DDS_SCALE = 65536

        # try to retrieve zone-specific data from mapping.
        try:
            fn, sourcesize, numtiles = texture_map[self.zoneID]
        except KeyError:
            print 'Zone %d not in texture_map' % self.zoneID
            raise
        else:
            fn += '.dds'
            DDS_SCALE = 65536 / numtiles
            
        sourcescale = 65536.0 / sourcesize
            
        texfilename = os.path.join(self.zone.filepath,'TerrainTex',fn)
        #print texfilename                   

        # Calculate the "interesting" range of background tiles for this
        # output tile
        if self.flip_x:
            xl = int((65536 - self.zone.IToRX(tile[2]) - (DDS_SCALE-1)) / DDS_SCALE)
            xh = int((65536 - self.zone.IToRX(tile[0])) / DDS_SCALE)
        else:
            xl = int(self.zone.IToRX(tile[0]) / DDS_SCALE)
            xh = int((self.zone.IToRX(tile[2]) + (DDS_SCALE-1)) / DDS_SCALE)

        if self.flip_y:
            yl = int((65536 - self.zone.IToRY(tile[3]) - (DDS_SCALE-1)) / DDS_SCALE)
            yh = int((65536 - self.zone.IToRY(tile[1])) / DDS_SCALE)
        else:
            yl = int(self.zone.IToRY(tile[1]) / DDS_SCALE)
            yh = int((self.zone.IToRY(tile[3]) + (DDS_SCALE-1)) / DDS_SCALE)

        #print 'xl=',xl,' xh=',xh,' yl=',yl, ' yh=',yh
        
        for y in xrange(yl, yh+1):
            if y < 0 or y > 7: continue
            if self.flip_y: basey = 65556 - (y+1) * DDS_SCALE
            else: basey = y * DDS_SCALE
            miny = self.zone.RToIY(basey)
            maxy = self.zone.RToIY(basey + DDS_SCALE)
            if maxy < tile[1] or miny > tile[3]: continue
            
            for x in xrange(xl, xh+1):
                if x < 0 or x > 7: continue
                if self.flip_x: basex = 65556 - (x+1) * DDS_SCALE
                else: basex = x * DDS_SCALE
                minx = self.zone.RToIX(basex)
                maxx = self.zone.RToIX(basex + DDS_SCALE)
                if maxx < tile[0] or minx > tile[2]: continue
 
                # Now jump through lots of hoops to avoid resizing the
                # entire source image (that kills us on very large scales,
                # regardless of the actual tile or region size, since at
                # e.g. scale=16384, each background image becomes a
                # 2048x2048 image...)

                # Calculate bounds of tile on this image
                srcbounds = [int((self.zone.IToRX(tile[0]) - basex) / sourcescale + 0.5) - 1,
                             int((self.zone.IToRY(tile[1]) - basey) / sourcescale + 0.5) - 1,
                             int((self.zone.IToRX(tile[2]) - basex) / sourcescale + 0.5) + 1,
                             int((self.zone.IToRY(tile[3]) - basey) / sourcescale + 0.5) + 1]

                # Crop to actual source dimensions
                if srcbounds[0] < 0: srcbounds[0] = 0
                if srcbounds[1] < 0: srcbounds[1] = 0
                if srcbounds[2] > sourcesize: srcbounds[2] = sourcesize
                if srcbounds[3] > sourcesize: srcbounds[3] = sourcesize
                if srcbounds[2] <= srcbounds[0] or srcbounds[3] <= srcbounds[1]: continue # no image on this tile.

                # Determine the projection of this source rectangle onto the destination image.
                destbounds = [self.zone.RToIX(basex + srcbounds[0] * sourcescale),
                              self.zone.RToIY(basey + srcbounds[1] * sourcescale),
                              self.zone.RToIX(basex + srcbounds[2] * sourcescale),
                              self.zone.RToIY(basey + srcbounds[3] * sourcescale)]

                # Determine what to resize the image to.
                resize_to = (destbounds[2] - destbounds[0],destbounds[3] - destbounds[1])

                # Clip destbounds against the actual tile. Remember where the clipping occurs.
                usebounds = [0,0,destbounds[2]-destbounds[0],destbounds[3]-destbounds[1]]
                if destbounds[0] < tile[0]:
                    usebounds[0] += tile[0] - destbounds[0]
                    destbounds[0] = tile[0]                    
                if destbounds[1] < tile[1]:
                    usebounds[1] += tile[1] - destbounds[1]
                    destbounds[1] = tile[1]
                if destbounds[2] > tile[2]:
                    usebounds[2] -= destbounds[2] - tile[2]
                    destbounds[2] = tile[2]
                if destbounds[3] > tile[3]:
                    usebounds[3] -= destbounds[3] - tile[3]
                    destbounds[3] = tile[3]
                #print tile, srcbounds, resize_to, usebounds, destbounds

                # Acquire and crop/resize/etc image
                i = Image.open(texfilename)
                    
                if self.flip_x: i = i.transpose(Image.FLIP_LEFT_RIGHT)
                if self.flip_y: i = i.transpose(Image.FLIP_TOP_BOTTOM)
                if self.zone.greyscale: i = i.convert('L')
                else: i = i.convert('RGB')

                i = i.crop(srcbounds)
                i = i.resize(resize_to, Image.BILINEAR)
                i = i.crop(usebounds)

                # Paste tile.
                destimage.paste(i, destbounds)

                    
    def renderTile(self, destimage, tile):

        texfilename = os.path.join(self.zone.filepath,
                                   'zone%03d' % self.zoneID,
                                   'tex%03d.mpk' % self.zoneID)
        if os.path.exists(texfilename):
            self.texfile = dempak.MPAKFile(texfilename)
            self.renderOldTexTile(destimage, tile)
        else:
            texfilename = os.path.join(self.zone.filepath,
                                   'zone%03d' % self.zoneID,
                                   'ter%03d.mpk' % self.zoneID)
            self.texfile = dempak.MPAKFile(texfilename)
            self.renderNewTerTile(destimage, tile)
        self.texfile.close()
        

# Changelog
# $Log: BackgroundRender.py,v $
# Revision 1.13  2004/08/11 16:07:36  cyhiggin
# sync with mapper-base
#
# Revision 1.7  2004/07/28 18:44:35  cyhiggin
# Added texture_map lookup table; took out search through textures.csv for new-style DDS file, as ocean zones use small repeating tiles, other zones use one big tile.
#
# Revision 1.6  2004/07/20 21:52:07  cyhiggin
# Added new rendering sub-methods to handle old and new-style background textures
#
# Revision 1.5  2004/06/12 04:45:25  cyhiggin
# Fixed flip_x bug that was affecting housing background textures.
#
# Revision 1.4  2004/03/31 17:24:00  cyhiggin
# Changed retrieval of flip_x and flip_y from config files to get, rather than stricter getboolean. As per merge with Calien's code
#
# Revision 1.3  2004/03/15 22:40:45  cyhiggin
# Revised Zone.filepath to not include zoneNNN directory, as is
# different for texture file sometimes.
#
