#!/usr/bin/env python
# 	$Id: mapper.py,v 1.15 2004/08/17 13:36:27 cyhiggin Exp $	

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

import datParser as ConfigParser

try:
    from PIL import Image, ImageFont, ImageDraw
    import gc
except ImportError as e:
    print("** Could not import PIL modules -- check PIL is installed **")
    print()
    raise

try:
    import dempak, Zone, BumpmapRender, FixtureRender, ContourRender, BackgroundRender, RiverRender, SolidRender, BoundsRender, GridRender, CaptionRender, GroveRender
    
except ImportError as e:
    print("** Could not import mapper support modules -- check your PYTHONPATH **")
    print()
    raise

#     module mapping render_map
#     format: 'renderer name' : RenderObject.RenderObject
render_map = {
    'bumpmap':    BumpmapRender.BumpmapRender,
    'fixture':    FixtureRender.FixtureRender,
#    'post-fixture': FixtureRender.FixtureRender,
    'contour':    ContourRender.ContourRender,
    'background': BackgroundRender.BackgroundRender,
    'river':      RiverRender.RiverRender,
    'solid':      SolidRender.SolidRender,
    'bounds':     BoundsRender.BoundsRender,
    'grid':       GridRender.GridRender,
    'caption':    CaptionRender.CaptionRender,
    'grove':      GroveRender.GroveRender
#    'altfixture': AltFixtureRender.FixtureRender
    }

def loadIncludes(settings):
    """Load any include files in settings file.

    Specifically, looks for any include directives in the 'maps'
    section and loads them.
    """
    files = []
    while 1:
        for o in settings.options('maps'):
            if o[:7] == 'include':
                files.extend(settings.get('maps', o).split(','))
                settings.remove_option('maps', o)

        if not files: break

        settings.read(files[0])
        del files[0]

def loadRenderers(settings):
    """Load needed renderer objects

    Load RendererObjects matching renderers specified in 'maps'
    section of settings file.
    """
    renderers = []

    namelist = settings.get('maps', 'renderers')

    names = [x.strip().lower() for x in namelist.split(',')]
    for name in names:
        type = settings.get(name, 'type').strip().lower()
        if type not in render_map:
            raise ConfigParser.Error('Unknown type "%s" for renderer "%s"' % (type, name))

        renderers.append((name, render_map[type]))

    return renderers

def drawByline(zone, out):
    """Draw byline on map

    Draw byline specified in settings file (if any), using bylinefont
    from settings file.
    """
    try:
        byline = zone.settings.get('maps', 'byline')
        font = ImageFont.load(zone.settings.get('maps', 'bylinefont'))
        draw = ImageDraw.Draw(out)
        size = font.getsize(byline)
	# Draw a black border
        draw.text( ((out.size[0] - size[0] - 5), (out.size[1] - size[1] - 5)-1), byline, font=font, fill=(0,0,0))
        draw.text( ((out.size[0] - size[0] - 5)+1, (out.size[1] - size[1] - 5)-1), byline, font=font, fill=(0,0,0))
        draw.text( ((out.size[0] - size[0] - 5)+1, (out.size[1] - size[1] - 5)), byline, font=font, fill=(0,0,0))
        draw.text( ((out.size[0] - size[0] - 5)+1, (out.size[1] - size[1] - 5)+1), byline, font=font, fill=(0,0,0))
        draw.text( ((out.size[0] - size[0] - 5), (out.size[1] - size[1] - 5)+1), byline, font=font, fill=(0,0,0))
        draw.text( ((out.size[0] - size[0] - 5)-1, (out.size[1] - size[1] - 5)+1), byline, font=font, fill=(0,0,0))
        draw.text( ((out.size[0] - size[0] - 5)-1, (out.size[1] - size[1] - 5)), byline, font=font, fill=(0,0,0))
        draw.text( ((out.size[0] - size[0] - 5)-1, (out.size[1] - size[1] - 5)-1), byline, font=font, fill=(0,0,0))
        # Then draw byline
        draw.text( (out.size[0] - size[0] - 5, out.size[1] - size[1] - 5), byline, font=font, fill=(255,255,255) )

        del draw
    except ConfigParser.NoOptionError: pass

def run(argv):
    """main run method of application

    Initializes config file parser,
    processes command-line settings,
    reads configuration from settings file,
    loads needed renderers,
    loads and initializes zone data,
    calls needed renderers,
    draws byline,
    saves output and exits.

    settings - configuration data from settings file
    zoneID - zone number
    zone - zone data object
    outpath - output file name
    
    """
    settings = ConfigParser.ConfigParser()
    scale = 512
    region = (0,0,65536,65536)
    outpath = None
    location = None
    zoneID = None

    print('mapper.py v.2.4')
    i = 1
    while i < len(argv):
        if argv[i] == '-settings':
            settings.read(argv[i+1])
            loadIncludes(settings)
            i += 1
        elif argv[i] == '-gamepath':
            settings.set('maps', 'gamepath', argv[i+1])
            i += 1
        elif argv[i] == '-polydir':
            settings.set('maps', 'polydir', argv[i+1])
            i += 1
        elif argv[i] == '-scale':
            try: scale = int(argv[i+1])
            except (ValueError,IndexError):
                print('-scale must be followed by a number')
                return 1
            i += 1
        elif argv[i] == '-location':
            location = argv[i+1]
            i += 1
        elif argv[i] == '-region':
            try:
                region = (int(argv[i+1]),int(argv[i+2]),int(argv[i+3]),int(argv[i+4]))
            except (ValueError,IndexError):
                print('-region must be followed by four numbers')
                return 1                
            i += 4
        elif argv[i] == '-zone':
            try:
                zoneID = int(argv[i+1])
            except (ValueError,IndexError):
                print('-zone must be followed by a number')
                return 1
            i += 1
        elif argv[i] == '-out':
            outpath = argv[i+1]
            i += 1
        elif argv[i] == '-renderers':
            settings.set('maps', 'renderers', argv[i+1])
            i += 1
        else:
            print("unknown option:", argv[i])
            return 1

        i += 1
    
    if not outpath:
        print("Please give an output filename (via -out <filename>)")
        return 1

    if not settings.has_section('maps'):
        print("No maps section found (did you specify -settings?)")
        return 1
    
    if location:
        lstr = settings.get('locations', location).split(',')
        zoneID = int(lstr[0])
        region = list(map(int,lstr[1:]))

    if zoneID is None:
        print("Please specify either -zone <zoneID> or -location <location>")
        return 1

    if region[0] < 0 or region[2] > 65536 or region[0] >= region[2] or region[1] < 0 or region[3] > 65536 or region[1] >= region[3]:
        print("Bad region " + repr(region) + ": must be 0..65536 in both dimensions")
        return 1
        
    imgregion = (scale * region[0] / 65536,
                 scale * region[1] / 65536,
                 scale * region[2] / 65536,
                 scale * region[3] / 65536)

    renderers = loadRenderers(settings)

    zone = Zone.Zone(settings, zoneID, scale, imgregion[:2])

    imagesize = (imgregion[2] - imgregion[0], imgregion[3] - imgregion[1])
    print('Mapping zone %d: %s to %s (%dx%d)' % (zoneID, repr(region), outpath, imagesize[0], imagesize[1]))
    zone.progress('Creating work area', 0.0)

    if zone.greyscale:
        out = Image.new('L', imagesize)
    else:
        out = Image.new('RGB', imagesize)
    for name, renderer in renderers:
        instance = renderer(zone, name)
        instance.render(out, (0,0,out.size[0],out.size[1]))
        del instance
        zone.progress(None)

    drawByline(zone, out)

    zone.progress('Writing ' + outpath, 0.0)
    out.save(outpath)
    zone.progress(None)
    del out
    del zone

    return 0

if __name__ == '__main__':
    import sys
    try:
        sys.exit(run(sys.argv))
    except ConfigParser.Error as e:
        print("Configuration error: " + repr(e))
        sys.exit(2)
    
# Change History:
# 
# $Log: mapper.py,v $
# Revision 1.15  2004/08/17 13:36:27  cyhiggin
# bringing up to date with mapper 2.4
#
# Revision 1.10  2004/08/17 13:34:43  cyhiggin
# updated version to 2.4 (live)
#
# Revision 1.9  2004/08/01 01:25:37  cyhiggin
# Started adding proper docstrings
# version now 2.3.4b
#
# Revision 1.8  2004/07/28 20:35:21  cyhiggin
# Updated version number to 2.3.3b
#
# Revision 1.7  2004/07/20 21:52:24  cyhiggin
# Updated version to 2.3.2
#
# Revision 1.6  2004/06/08 21:04:05  cyhiggin
# Updated patch level.
#
# Revision 1.5  2004/05/27 14:04:03  cyhiggin
# Added GroveRender, renderer for tree clusters/groves to mapper.
#
# Revision 1.4  2004/05/13 02:08:44  cyhiggin
# Added version line.
#
# Revision 1.3  2004/04/01 17:52:25  cyhiggin
# Merged NIF4 and path adjustments from Calien into mapper codebase
#
# Revision 1.2  2004/03/15 22:25:05  cyhiggin
# Added search for phousing zones. Added attribute 'filepath' to Zone
# class to hold path to zone files.
#
# 25/3/2002 G. Willoughby <sab@freeuk.com>
# lines 55-64 added black border
# line 147: added '"JPEG", quality=100' to the save method

