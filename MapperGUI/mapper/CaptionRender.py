# CaptionRender.py: DAoC mapper, text captioning
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
#   font: path to a .pil file containing the font to use
#   color: color to draw the captions in
#   source: name of the section containing caption info. This should contain
#        options of the form 'zoneID,x,y = caption text'

import ImageDraw, ImageFont

class CaptionRender:
    def __init__(self, zone, name):
        self.zone = zone
        self.name = name

        sources = zone.settings.get(name, 'source').split(',')

        self.font = ImageFont.load(zone.settings.get(name, 'font'))
        self.color = zone.getColor(name, 'color', (255,255,255))
        self.captions = []

        for source in sources:
            for o in zone.settings.options(source):
                zoneID,x,y = map(int, o.split(','))
                if zoneID != zone.zoneID: continue
                text = zone.settings.get(source, o)
                self.captions.append( (x,y,text) )

    def render(self, destimage, region):
        draw = ImageDraw.Draw(destimage)
        l = len(self.captions)
        for i in xrange(l):
            self.zone.progress(self.name, float(i) / l)

            x,y,text = self.captions[i]
            textsize = self.font.getsize(text)
            ix,iy = self.zone.RToI((x,y))
            
	    # Draw a black border
            draw.text(((ix - textsize[0]/2),
                       (iy - textsize[1]/2)-1), text, font=self.font, fill=(0,0,0))
            draw.text(((ix - textsize[0]/2)+1,
                       (iy - textsize[1]/2)-1), text, font=self.font, fill=(0,0,0))
            draw.text(((ix - textsize[0]/2)+1,
                       (iy - textsize[1]/2)), text, font=self.font, fill=(0,0,0))
            draw.text(((ix - textsize[0]/2)+1,
                       (iy - textsize[1]/2)+1), text, font=self.font, fill=(0,0,0))
            draw.text(((ix - textsize[0]/2),
                       (iy - textsize[1]/2)+1), text, font=self.font, fill=(0,0,0))
            draw.text(((ix - textsize[0]/2)-1,
                       (iy - textsize[1]/2)+1), text, font=self.font, fill=(0,0,0))
            draw.text(((ix - textsize[0]/2)-1,
                       (iy - textsize[1]/2)), text, font=self.font, fill=(0,0,0))
            draw.text(((ix - textsize[0]/2)-1,
                       (iy - textsize[1]/2)-1), text, font=self.font, fill=(0,0,0))

            # Draw the text already!
            draw.text((ix - textsize[0]/2, iy - textsize[1]/2),
                      text, font=self.font, fill=self.color)
            
# Change History:
# 
# 25/3/2002 G. Willoughby <sab@freeuk.com>
# lines 65-73 added black border
