#!/usr/bin/python

# glue.py: script to scale & glue maps to produce an imagemap & overview
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

# Updated: 2002/10/28

import Image, ImageDraw, ImageFont, ConfigParser, os
import dempak

def draw_with_border(draw, name, xypos, font, col, borderfill ):
    # draw white border
    ix, iy = xypos
    
    pos = (ix, iy-1)
    draw.text(pos,name, font=font, fill=borderfill)
    pos = (ix+1, iy-1)
    draw.text(pos,name, font=font, fill=borderfill)
    pos = (ix+1, iy)
    draw.text(pos,name, font=font, fill=borderfill)
    pos = (ix+1, iy+1)
    draw.text(pos,name, font=font, fill=borderfill)
    pos = (ix, iy-1)
    draw.text(pos,name, font=font, fill=borderfill)
    pos = (ix-1,iy+1)
    draw.text(pos,name, font=font, fill=borderfill)
    pos = (ix-1, iy)
    draw.text(pos,name, font=font, fill=borderfill)
    pos = (ix-1, iy-1)
    draw.text(pos,name, font=font, fill=borderfill)
    
    # draw text
    draw.text(xypos, name, font=font, fill=col )


class Zone:
    def __init__(self, cp, section, infile, font, scale):
        self.id = int(section[4:])
        self.name = cp.get(section, 'name')
        self.x = int(cp.get(section, 'region_offset_x'))
        self.y = int(cp.get(section, 'region_offset_y'))
        self.w = int(cp.get(section, 'width'))
        self.h = int(cp.get(section, 'height'))
        try:
            size = (scale*self.w, scale*self.h)
            self.map = Image.open(infile).resize(size, Image.BILINEAR)
            #col = (192,192,255)
            col = (255,64,64)
            borderfill = (255,255,255)
            draw = ImageDraw.Draw(self.map);
            textsize = draw.textsize(self.name, font=font)
            if textsize[0] < size[0]*0.8:
                pos = (size[0]/2 - textsize[0]/2, size[1]/2 - textsize[1]/2)
                draw_with_border(draw, self.name, pos, font, col, borderfill)
            else:
                words = self.name.split(' ')
                l = len(words)
                text1 = ' '.join(words[:l/2])
                text2 = ' '.join(words[l/2:])
                textsize = draw.textsize(text1, font=font)
                pos = (size[0]/2 - textsize[0]/2, size[1]/2 - textsize[1])
                draw_with_border(draw, text1, pos, font, col, borderfill)
                
                textsize = draw.textsize(text2, font=font)
                pos = (size[0]/2 - textsize[0]/2, size[1]/2)
                draw_with_border(draw, text2, pos, font, col, borderfill)
                
            del draw
        except IOError, e:
            self.map = None

def glue(argv):
    region = None
    target = None
    gamepath = None

    scale = 10
    fontpath = 'data/6x12-ISO8859-1.pil'
    imagetemplate = 'out/map%03d_o.png'

    i = 1
    while i < len(argv):
        if argv[i] == '-gamepath':
            gamepath = argv[i+1]
            i += 2
        elif argv[i] == '-out':
            target = argv[i+1]
            i += 2
        elif argv[i] == '-region':
            region = int(argv[i+1])
            i += 2
        elif argv[i] == '-fontpath':
            fontpath = argv[i+1]
            i += 2
        elif argv[i] == '-scale':
            scale = int(argv[i+1])
            i += 2
        elif argv[i] == '-template':
            imagetemplate = argv[i+1]
            i += 2
        else:
            print "Unknown option:", argv[i]
            return 1

    if not gamepath or not target or region is None:
        print "Syntax: %s -gamepath <path> -out <outfile> -region <regionID>"
        print " [-scale <factor>] [-fontpath <path>] [-template <imagetemplate>]"
        print " Reads images based on imagetemplate % zoneID. Writes <outfile>."
        print " Writes an imagemap to stdout."
        return 1

    font = ImageFont.load(fontpath)

    cp = ConfigParser.ConfigParser()
    try:
        cp.readfp(dempak.getMPAKEntry(os.path.join(gamepath, 'zones', 'zones.mpk'), 'zones.dat'))
    except ConfigParser.ParsingError: pass

    zones = []

    for s in cp.sections():
        if s[:4] == 'zone' and cp.getint(s, 'region') == region and cp.getint(s, 'enabled') == 1:
            try: type = cp.getint(s, 'type')
            except ConfigParser.NoOptionError: type = 0
            if type != 0 and type != 3: continue
#            print "Loading " + s + " ..."
            z = Zone(cp, s, imagetemplate % int(s[4:]), font, scale)
#            print " .. @", (z.x, z.y), "+", (z.w, z.h)
            zones.append(z)            

    min_x = max_x = min_y = max_y = None
    for z in zones:
        if not z.map: continue
        
        if min_x is None:
            min_x = z.x
            max_x = z.x + z.w
            min_y = z.y
            max_y = z.y + z.h
        else:
            if z.x < min_x: min_x = z.x
            if z.x + z.w > max_x: max_x = z.x + z.w
            if z.y < min_y: min_y = z.y
            if z.y + z.h > max_y: max_y = z.y + z.h

    if not min_x:
        #print "No zones to process."
        return

    size = ( (max_x - min_x) * scale, (max_y - min_y) * scale )

    #print "Output image size is", size

    out = Image.new('RGBA', size, (0,0,0,0))

    print '<map name="%s">' % os.path.basename(target)

    for z in zones:
        print '<area shape="rect" coords="%d,%d,%d,%d" href="%s" alt="%s">' % \
        ((z.x - min_x) * scale, (z.y - min_y) * scale,
         (z.x + z.w - min_x) * scale, (z.y + z.h - min_y) * scale,
         'map%03d.jpg' % z.id, z.name)
        #print "Pasting %d..." % z.id
        out.paste(z.map, ((z.x - min_x) * scale, (z.y - min_y) * scale))

    print '</map>'
    
    out.save(target, quality=80)

if __name__ == '__main__':
    import sys
    sys.exit(glue(sys.argv))

# Change History:
#
# 
