# GridRender.py: DAoC mapper, coordinate grid overlay
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
#  interval:  set the interval (in map coordinates) of the grid
#  color:     set the color to draw the grid in
#  alpha:     set the transparency of the grid
#  font:      if set, draw coordinate labels using this .pil font
#  fontcolor: if font is set, draw coordinate labels in this color

import Tiler
from PIL import Image, ImageDraw, ImageFont
import datParser as ConfigParser

class GridRender(Tiler.Tiler):
    def __init__(self, zone, name):
        Tiler.Tiler.__init__(self, zone, name)

        try: self.interval = zone.settings.getint(name, 'interval')
        except ConfigParser.NoOptionError: self.interval = 10000

        try: self.alpha = zone.settings.getint(name, 'alpha')
        except ConfigParser.NoOptionError: self.alpha = 50

        self.color = zone.getColor(name, 'color', (0,0,0))

        try:
            self.font = ImageFont.load(zone.settings.get(name, 'font'))
            self.fontcolor = zone.getColor(name, 'fontcolor', (255,255,255))
        except ConfigParser.NoOptionError:
            self.font = None

    # This makes things a bit easier..
    def render(self, dest, region):
        Tiler.Tiler.render(self, dest, region)

        if self.font:
            draw = ImageDraw.Draw(dest)

            for y in xrange(0,65536,self.interval):
                yv = self.zone.RToIY(y)
                text = ' %d' % y
                textsize = self.font.getsize(text)
                draw.text((0, yv - textsize[1]), text, fill=self.fontcolor, font=self.font)

            for x in xrange(0,65536,self.interval):
                xv = self.zone.RToIX(x)
                text = '%d ' % x
                textsize = self.font.getsize(text)

                # bleh. PIL has no text rotation drawing thing.
                tempimage = Image.new('1', textsize)
                tempdraw = ImageDraw.Draw(tempimage)
                tempdraw.text((0,0), text, fill=1, font=self.font)
                del tempdraw
                tempimage = tempimage.transpose(Image.ROTATE_90)
                destregion = (xv, 0, xv + textsize[1], textsize[0])
                dest.paste(self.fontcolor, destregion, tempimage)
                del tempimage        
        
    def renderTile(self, dest, tile):
        i = Image.new('L', (tile[2] - tile[0], tile[3] - tile[1]))
        draw = ImageDraw.Draw(i)

        for x in xrange(0,65536,self.interval):
            xv = self.zone.RToIX(x) - tile[0]
            draw.line(((xv,0), (xv,65536)), fill=self.alpha)
        
        for y in xrange(0,65536,self.interval):
            yv = self.zone.RToIY(y) - tile[1]
            draw.line(((0,yv), (65536,yv)), fill=self.alpha)

        dest.paste(self.color, tile, i)
        del draw
        del i
