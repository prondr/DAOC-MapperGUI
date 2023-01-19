# $Id: Zone.py,v 1.13 2004/08/11 16:07:36 cyhiggin Exp $	
# Zone.py: DAoC mapper, shared zone representation
# See http://www.randomly.org/projects/mapper/ for updates and sample output.
# Also see http://nathrach.republicofnewhome.org/

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

import os, sys
from PIL import Image
import dempak, Util
import datParser as ConfigParser

class Zone:
    """This class holds the shared data that various renderers use to extract
    additional information about the zone and do coordinate translation.
    It also maintains a shared heightmap.
    """
    def __init__(self, settings, zoneID, scale, origin):
        self.gamepath = settings.get('maps', 'gamepath')
        self.zoneID = zoneID
        self.scale = scale / 65536.0
        self.origin = origin
        self.settings = settings
        # added river variables to control 2nd fixture rendering pass.
        self.riverheight = []
        self.riverdone = 0
        
        self.filepath = os.path.join(self.gamepath, 'zones')
        if not os.path.exists(os.path.join(self.filepath,'zone%03d' % zoneID)):
            self.filepath =  os.path.join(self.gamepath, 'phousing','zones')
            if not os.path.exists(os.path.join(self.filepath,'zone%03d' % zoneID)):
                self.filepath =  os.path.join(self.gamepath, 'frontiers','zones')
                
        self._datfile = dempak.MPAKFile(os.path.join(self.filepath,
                                                     'zone%03d' % zoneID,
                                                     'dat%03d.mpk' % zoneID))
            
        try:
            self._csvfile = dempak.MPAKFile(os.path.join(self.filepath,
                                                         'zone%03d' % zoneID,
                                                         'csv%03d.mpk' % zoneID))
        except IOError:
            self._csvfile = None
          
        self.sector_dat = ConfigParser.ConfigParser()
        try:
            self.sector_dat.readfp(self.datafile('sector.dat'))
        except ConfigParser.ParsingError:
            pass
            
        self.heightmap = None

        try:
            mode = settings.get('maps', 'mode').lower()

            # don't you love english?
            if mode == 'greyscale' or mode == 'grayscale': self.greyscale = 1
            elif mode == 'color' or mode == 'colour': self.greyscale = 0
            else: raise RuntimeError('unknown maps.mode=' + mode)
        except ConfigParser.NoOptionError: self.greyscale = 0

        try: self.tilesize = settings.getint('maps', 'tilesize')
        except ConfigParser.NoOptionError: self.tilesize = 64

        try: self.polydir = settings.get('maps', 'polydir')
        except ConfigParser.NoOptionError: self.polydir = 'polys'

        self.laststage = None

    def datafile(self, name):
        if self._csvfile:
            try: return self._csvfile.open(name)
            except IOError as e: pass

        return self._datfile.open(name)

    def IToR(self, imagept):
        return (self.IToRX(imagept[0]),
                self.IToRY(imagept[1]))

    def RToI(self, realpt):
        return (self.RToIX(realpt[0]),
                self.RToIY(realpt[1]))

    def IToRX(self, x):
        return int((x + self.origin[0]) / self.scale)

    def IToRY(self, y):
        return int((y + self.origin[1]) / self.scale)

    def RToIX(self, x):
        return int(x * self.scale - self.origin[0])

    def RToIY(self, y):
        return int(y * self.scale - self.origin[1])

    def RToIScale(self, realsize):
        return realsize * self.scale
    
    def IToRScale(self, pixels):
        return pixels / self.scale
    
    def loadHeightmap(self):
        """Create heightmap from terrain.pcx and offset.pcx files in data.
        """
        if self.heightmap: return
    
        terrainscale = int(self.sector_dat.get('terrain', 'scalefactor'))
        offsetscale = int(self.sector_dat.get('terrain', 'offsetfactor'))

        terrainmap = Image.open(self.datafile('terrain.pcx'))
        assert terrainmap.size == (256,256)
        assert terrainmap.mode == 'L'

        offsetmap = Image.open(self.datafile('offset.pcx'))
        assert offsetmap.size == (256,256)
        assert offsetmap.mode == 'L'

        hm = Image.new('I', (256, 256))
        for x in xrange(256):
            self.progress('Generating heightmap', x/256.0)
            for y in xrange(256):
                height = terrainmap.getpixel( (x,y) ) * terrainscale + offsetmap.getpixel( (x,y) ) * offsetscale
                hm.putpixel( (x,y), height )

        self.heightmap = hm
        del offsetmap
        del terrainmap

    def getHeightmapRegion(self, region):
        """region is in image pixels
        """
        self.loadHeightmap()
        return Util.Scale256(self, self.heightmap, region)
    
    def progress(self, stage, frac=0.0):
        if stage != self.laststage:
            if self.laststage:
                sys.stdout.write('(100%)\n')        
            self.laststage = stage

            if not stage: return
            sys.stdout.write(stage + " ... \n")

        pcnt = '(%d%%)\n' % int(frac * 100.0)
        #pcnt += '\b' * len(pcnt)
        sys.stdout.write(pcnt)
        sys.stdout.flush()

    def getColor(self, section, key, default):
        try:
            s = self.settings.get(section, key)
            if s.lower() == 'none': return None
            if s.lower() != 'default':
                col = tuple(map(int, s.split(',')))
                
                if len(col) == 1:
                    col = (col[0] / 0.299, col[0] / 0.587, col[0] / 0.114)
                elif len(col) == 3:
                    col = col + (255,)
                elif len(col) == 4:
                    pass
                else:
                    raise RuntimeError('bad color in ' + section + '.' + key + ': expected a 3-tuple or 4-tuple')
            else:
                col = default
        except ConfigParser.NoOptionError:
            col = default

        if self.greyscale:
            return (col[0] * 0.299 + col[1] * 0.587 + col[2] * 0.114)
        else:
            return tuple(col)

# Change History:
# 
# $Log: Zone.py,v $
# Revision 1.13  2004/08/11 16:07:36  cyhiggin
# sync with mapper-base
#
# Revision 1.8  2004/08/06 21:40:17  cyhiggin
# zone.riverheight is now a list of all riverheights in the zone
#
# Revision 1.7  2004/08/02 04:26:06  cyhiggin
# Added more docstrings
#
# Revision 1.6  2004/08/01 01:05:21  cyhiggin
# Added riverdone and riverheight variables. Initialized them.
# Started adding proper docstrings.
#
# Revision 1.5  2004/06/08 21:02:56  cyhiggin
# Made more forgiving of parsing errors in sector.dat
#
# Revision 1.4  2004/05/11 17:24:28  cyhiggin
# Added New Frontiers path to possible filepaths.
#
# Revision 1.3  2004/03/15 22:40:45  cyhiggin
# Revised Zone.filepath to not include zoneNNN directory, as is
# different for texture file sometimes.
#
# Revision 1.2  2004/03/15 22:25:05  cyhiggin
# Added search for phousing zones. Added attribute 'filepath' to Zone
# class to hold path to zone files.
#
# 24/3/2002 G. Willoughby <sab@freeuk.com>
# line 131: added a '\n' to the end
# line 133: added a '\n' to the end of 'pcnt'
# line 134: commented out
