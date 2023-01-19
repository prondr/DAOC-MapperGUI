# $Id: FixtureRender.py,v 1.16 2004/08/11 16:07:36 cyhiggin Exp $
# FixtureRender.py: DAoC mapper, fixture (structures/objects) rendering
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
#   classify: name of section containing 'name=type' options used to classify
#     fixtures by .nif filename
#   <type>=<method>: draw fixtures classified as 'type' via the fixture
#     rendering option in section 'method'
#   <file>=<method>: draw 'file'.nif using method 'method'

# Method section options:
#    layer=n:        controls fixture drawing order
#
#    type=none:         don't draw fixture at all
#    type=wireframe:    draw only fixture wireframe
#      color=<color>:   draw wireframe in this color
#    type=solid:        draw the fixture wireframe, filled
#      fill=<color>:    fill with this color
#      outline=<color>: outline the wireframe with this color
#    type=shaded:       draw the fixture flat-shaded
#      color=<color>:   use this color as the base color

import re, math, os, stat, sys
import datParser as ConfigParser
import Image, ImageDraw
import NIFToPoly, Tiler, dempak, Util

#
# NIF renderers
#

class ShadedNIF:
    """Contains methods for drawing flat-shaded models

    member data:
       layer - layer specified in settings.
       polys - final polygon list
       color - color of model.
       lv - lv from settings
       lmin - lmin from settings
       lmax - lmax from settings
       maxz - max z coord of model
       radius - outside radius of model.
    """
    def __init__(self, color, polylist, layer, lv, lmin, lmax):
        """initialize ShadedNIF

        initializes ShadedNIF with
        color = color,
        polylist = polygon list of NIF,
        layer = layer of drawing
        lv = lv
        lmin = light min
        lmax = light max
        and finds outside parameters of model from polylist.
        """
        self.layer = layer
        self.polys = []
        self.color = color
        self.lv = lv
        self.lmin = lmin
        self.lmax = lmax

        minx = None
        self.maxz = None
        for poly in polylist:
            # face normal
            n = Util.normalize(Util.normal(poly[0], poly[1], poly[2]))
            
            # backface cull
            if n[2] < 0.0: continue

            # shade face
            nzlz = n[2] * lv[2]

            # sort faces on z
            plist = []
            local_maxz = poly[0][2]
            for x,y,z in poly:
                if not minx:
                    minx = maxx = x
                    miny = maxy = y
                else:
                    if x < minx: minx = x
                    elif x > maxx: maxx = x
                    if y < miny: miny = y
                    elif y > maxy: maxy = y

                if z > local_maxz: local_maxz = z                    
                plist.append( (x,y) )
                
            l = (local_maxz, n[0:2], nzlz, tuple(plist))
            self.polys.append(l)

            if not self.maxz or local_maxz > self.maxz:
                self.maxz = local_maxz

        self.polys.sort()

        r1 = math.sqrt(minx*minx + miny*miny)
        r2 = math.sqrt(maxx*maxx + maxy*maxy)
        if r1 > r2: self.radius = r1
        else: self.radius = r2

    def draw(self, zone, canvas, ox, oy, a, mag):
        """Draw the model with flat-shading.

        Draw the model on canvas with
        zone = zone object
        canvas = canvas widget
        ox = original x coord in zone data
        oy = original y coord in zone data
        a = angle? altitude?
        mag = ?
        """
        sina = math.sin(a * math.pi / 180.0)
        cosa = math.cos(a * math.pi / 180.0)

        # draw in Z order
        for dummy, normal, nzlz, plist in self.polys:
            # note we effectively flip the Y sign here to
            # compensate for geometry vs. screen Y axis having
            # different signs

            rn = (normal[0] * cosa + normal[1] * sina,
                  normal[0] * sina - normal[1] * cosa)                
            
            ndotl = nzlz + rn[0] * self.lv[0] + rn[1] * self.lv[1]
            if ndotl > 0.0: ndotl = 0.0
            lighting = self.lmin - (self.lmax - self.lmin) * ndotl
            
            if zone.greyscale:
                shade = self.color * lighting
            else:
                shade = (self.color[0] * lighting,
                         self.color[1] * lighting,
                         self.color[2] * lighting,
                         self.color[3])
                    
            pl = []
            for x,y in plist:
                # note we effectively flip the Y sign here to
                # compensate for geometry vs. screen Y axis having
                # different signs
                newX = ox + (x * cosa + y * sina) * mag / 100
                newY = oy + (x * sina - y * cosa) * mag / 100
                pl.append( (zone.RToIScale(newX), zone.RToIScale(newY)) )

            canvas.polygon(pl, fill=shade, outline=shade)

class PolyNIF:
    """Contains methods for drawing solid-colored models.

    member data:
       layer - layer specified in settings.
       polylist - final polygon list
       fill - solid fill color
       outline - outline color
       maxz - max z coord of model
       radius - outside radius of model.
    """
    def __init__(self, outline, fill, polylist, layer):
        """initialize PolyNIF

        Initializes PolyNIF with:
        fill = fill color
        polylist = polygon list
        layer = layer
        outline = outline color
        and finds outside radius of model.
        """

        self.fill = fill
        self.outline = outline
        self.polylist = polylist
        self.layer = layer
        self.maxz = 0

        minx = None
        for poly in polylist:
            for x,y,z in poly:
                if not minx: minx = maxx = miny = maxy = x
                else:
                    if x < minx: minx = x
                    elif x > maxx: maxx = x
                    if y < miny: miny = y
                    elif y > maxy: maxy = y

        r1 = math.sqrt(minx*minx + miny*miny)
        r2 = math.sqrt(maxx*maxx + maxy*maxy)
        if r1 > r2: self.radius = r1
        else: self.radius = r2

    def draw(self, zone, canvas, ox, oy, a, mag):
        """Draw PolyNIF object
        
        Draws model on canvas using:
        zone = zone data
        canvas = canvas widget
        ox = original x coord in zone data
        oy = original y coord in zone data
        a = angle? altitude?
        mag = ?
        """

        sina = math.sin(a * math.pi / 180.0)
        cosa = math.cos(a * math.pi / 180.0)

        for poly in self.polylist:
            pl = []
            for x,y,z in poly:
                # note we effectively flip the Y sign here to
                # compensate for geometry vs. screen Y axis having
                # different signs
                newX = ox + (x * cosa + y * sina) * mag / 100
                newY = oy + (x * sina - y * cosa) * mag / 100
                pl.append( (zone.RToIScale(newX), zone.RToIScale(newY)) )

            canvas.polygon(pl, fill=self.fill, outline=self.outline)

class MissingNIF:
    """Contains methods for handling missing models.
    """
    def __init__(self, file):
        """initializes MissingNIF to nominal values.
        """
        self.file = file
        self.layer = 1
        self.warned = 0
        self.radius = 0
        self.maxz = 0
    
    def draw(self, zone, canvas, ox, oy, a, mag):
        """Warns of missing NIF file and flags warning.
        """
        if not self.warned:
            print "warning: use of missing NIF " + self.file
            self.warned = 1


def findtheStupidNPKfile(zone, file):
    """find the NIF model archive (NPK file)

    Cycles through the various directories known to contain NIF archives,
    and a variety of capitalization schemes, given:
    zone - zone data object
    file - base name of NIF file to be found.
    """
    speelings = [file, file.capitalize(), file.upper()]
    for myfname in speelings:
        # First, we try variations on NIF directory...
        nifdir = os.path.join(zone.gamepath, 'zones', 'zone%03d' % zone.zoneID, 'nifs')
        # try capitalized...
        if not os.path.exists(nifdir):
            nifdir = os.path.join(zone.gamepath, 'zones', 'zone%03d' % zone.zoneID, 'NIFS')
        # now test with file name
        npkpath = os.path.join(nifdir, myfname + '.npk')
        # we found it?
        if os.path.exists(npkpath):
            break

        # we didn't find it -- either in global Nifs directory, or other speeling.
        npkpath = os.path.join(zone.gamepath, 'zones', 'Nifs', myfname + '.npk')
        if os.path.exists(npkpath):
            break
        
        # lower-case 'nifs' ?
        npkpath = os.path.join(zone.gamepath, 'zones', 'nifs', myfname + '.npk')
        if os.path.exists(npkpath):
            break
            
        # maybe it's a tree? (getting desperate here...)
        npkpath = os.path.join(zone.gamepath, 'zones', 'Trees', myfname + '.npk')
        if os.path.exists(npkpath):
            break

        # try frontiers/nifs?  
        npkpath =  os.path.join(zone.gamepath,'frontiers','nifs', myfname + '.npk')
        if os.path.exists(npkpath):
            break
                   
        # try phousing/nifs?  (beyond desperate!)
        npkpath =  os.path.join(zone.gamepath,'phousing','nifs',
                                myfname + '.npk')
        if os.path.exists(npkpath):
            break

    if not os.path.exists(npkpath):
        print 'Did not find NPK for %s' % file
        
    return npkpath

# place to stash poly lists we've already loaded this run
_cache = {}


def readPolys(zone, file):
    """Polygon loader

    Find the NIF (model) file and load the polygon list from it.
    If already cached, retrieve it from cache and exit.
    Otherwise, must extract polygon list from NIF file using
    NIFtoPoly()
    """
    # We try to be smart about mtimes here.

    # Locate the right .npk
    npkpath = findtheStupidNPKfile(zone,file)
    if npkpath.find('zone%03d' % zone.zoneID) > 0:
        polypath = os.path.join(zone.polydir, file + ".%03d.poly" % zone.zoneID)
    else:
        polypath = os.path.join(zone.polydir, file + ".poly")
        
    if _cache.has_key(polypath):
        return _cache[polypath]

    try:
        poly_mtime = os.stat(polypath)[stat.ST_MTIME];
        poly_ok = 1
    except OSError, e:
        poly_mtime = 0
        poly_ok = 0

    try:
        npk_mtime = os.stat(npkpath)[stat.ST_MTIME]
        npk_ok = 1
    except OSError, e:
        npk_mtime = 0
        npk_ok = 0
        
    polylist = None
    
    if npk_mtime > poly_mtime and npk_ok:
        # Need to recreate the .poly file.
        try:
            sys.stdout.write("Converting " + npkpath + " to " + polypath + " ...\n")
            npk = dempak.MPAKFile(npkpath)            
            nif = npk.open(file + '.nif')
            
            nifdata = nif.read()
            nif.close()
            npk.close()
            try:
                nodemap, first = NIFToPoly.load(nifdata)
            except:
                print 'Could not load NIF %s from %s' % (file + '.nif', npkpath)
                polylist = None
                return polylist
            
            polylist = nodemap[first].poly(nodemap, NIFToPoly.null_xform)
            del nodemap
            del first

            # We don't really care if this fails.
            if not os.path.isdir(zone.polydir): os.mkdir(zone.polydir)
            NIFToPoly.savePolys(polylist, polypath)
        except (NIFToPoly.error, IOError):
            import traceback
            traceback.print_exc()

    if not polylist and poly_ok:
        try:
            polylist = NIFToPoly.loadPolys(polypath)
        except IOError, e:
            import traceback
            traceback.print_exc()

    _cache[polypath] = polylist

    return polylist


class FixtureRender(Tiler.Tiler):
    """Renderer class for structures, decor, trees, etc. (fixtures).

    member data:
       nifmap - mapping of NIF ID to NIF objects
       zone - associated zone object
       layers - array[layers] of fixture data tuples: (zkey,x,y,a,mag,nif)
    """
    def __init__(self, zone, name):
        """Initialize FixtureRender as child class of Tiler.Tiler
        """
        Tiler.Tiler.__init__(self, zone, name)

    def preRender(self):
        """Setup to do before actual rendering.
        """
        self.readNIFs()
        self.readFixtures()
        if self.zone.riverdone:
            self.preRiverCheck()

    # compiled regular expression for parsing nif file names in nifs.csv
    _re_NIF = re.compile(r'(\d+),[^,]+,([^,]+)\.(nif),\d+,\d+,(\d+),.*', re.IGNORECASE)
    
    def readNIFs(self):
        """Read list of models (NIFS) for rendering.

        Gets NIFs and initializes appropriate NIF object (ShadedNIF, PolyNIF, MissingNIF).
        Also builds mapping of NIF id to NIF object. (member nifmap)
        """
        try: classify = self.zone.settings.get(self.name, 'classify')
        except ConfigParser.NoOptionError: classify = None
        
        self.nifmap = {}
        nifs = self.zone.datafile('nifs.csv')
        for l in nifs.readlines():
            match = FixtureRender._re_NIF.match(l)
            if match:
                try:
                    id, file, nifext, color = match.groups()
                except ValueError, inst:
                    sys.stderr.write( "ValueError: %s" % str(inst.args))
                    sys.stderr.write( match.groups())
                    continue;
                id = int(id)
                color = int(color)

                # Classify the NIF.
                classname = file
                if classify:
                    try:
                        classname = self.zone.settings.get(classify, file)
                    except ConfigParser.NoOptionError:
                        pass

                try:
                    variant = self.zone.settings.get(self.name, classname)
                except ConfigParser.NoOptionError:
                    variant = self.zone.settings.get(self.name, 'default')

                # Find settings.
                type = self.zone.settings.get(variant, 'type').lower().strip()
                if type == 'none':
                    self.nifmap[id] = None
                    continue

                if color == 0: default = (255, 255, 255, 255)
                else: default = (color%256, (color/256)%256, color/65536, 255)
                layer = self.zone.settings.getint(variant, 'layer')

                firstpass = 2
                while firstpass:
                    firstpass -= 1
                    polylist = readPolys(self.zone, file)
                    if polylist:
                        if type == 'wireframe':
                            color = self.zone.getColor(variant, 'color', default)
                            self.nifmap[id] = PolyNIF(color, None, polylist, layer)
                            break
                        elif type == 'solid':
                            o = self.zone.getColor(variant, 'outline', default)
                            f = self.zone.getColor(variant, 'fill', default)
                            self.nifmap[id] = PolyNIF(o, f, polylist, layer)
                            break
                        elif type == 'shaded':                        
                            color = self.zone.getColor(variant, 'color', default)
                            try:
                                s = self.zone.settings.get(variant, 'light_vect')
                                lv = map(float, s.split(','))
                            except ConfigParser.NoOptionError:
                                lv = (-1.0,1.0,-1.0)
                            lv = Util.normalize(lv)

                            try:
                                lmin = float(self.zone.settings.get(variant, 'light_min'))
                            except ConfigParser.NoOptionError:
                                lmin = 0.5
                            try:
                                lmax = float(self.zone.settings.get(variant, 'light_max'))
                            except ConfigParser.NoOptionError:
                                lmax = 1.0

                            self.nifmap[id] = ShadedNIF(color, polylist, layer, lv, lmin, lmax)
                            break
                        else:
                            raise RuntimeError, 'unknown NIF type: ' + type
                    elif (self.name=='trees') and (firstpass > 0):
                        try:
                            print 'Checking for alternate tree to %s' % file
                            file = self.zone.settings.get(variant,'defaulttree')
                            continue        
                        except ConfigParser.NoOptionError:
                            self.nifmap[id] = MissingNIF(file)
                            break
                    else:
                        self.nifmap[id] = MissingNIF(file)
                        break
            
        nifs.close()

    _re_Fixture = re.compile(r'\d+,(\d+),[^,]+,(\d+),(\d+),(\d+),(\d+),(\d+),.*')
    def readFixtures(self):
        """Read list of fixtures from fixtures.csv

        Gets fixtures to be plotted on map and their coordinates on map.
        """
        self.layers = {}
        fixtures = self.zone.datafile('fixtures.csv')
        for l in fixtures.readlines():
            match = FixtureRender._re_Fixture.match(l)
            if match:
                nifId = int(match.group(1))
                try:
                    nif = self.nifmap[nifId]
                except KeyError, inst:
                    print "KeyError:", inst.args
                    print "    from fixtures.csv: " + l
                    continue
                
                if not nif: continue
                x = int(match.group(2))
                y = int(match.group(3))
                z = int(match.group(4))
                a = int(match.group(5))
                mag = int(match.group(6))
                zkey = nif.maxz * z

                # if this is 2nd pass, don't want to re-render above-water objects.
                if self.zone.riverdone:
                    if (z + 100) > max(self.zone.riverheight):
##                         print 'skipping abovewater NIF %d at %d,%d,%d' % (nifId,x,y,z)
                        continue
                    
                data = (zkey,x,y,z,a,mag,nif)

                if self.layers.has_key(nif.layer):
                    self.layers[nif.layer].append(data)
                else:
                    self.layers[nif.layer] = [data]

        fixtures.close()

        layers = self.layers.keys();
        layers.sort()
        for layer in layers:
            self.layers[layer].sort()


    def preRiverCheck(self):
        """Stuff to do before doing rest of check for waterline structures

        Get heightmap parameters
        """
        self.zone.loadHeightmap()
        self.minheight, self.maxheight = self.zone.heightmap.getextrema()

    
    def renderTile(self, destimage, tile):
        """Actually draw the models on the map

        Matches fixtures to NIF data and draws NIFS at fixture coords,
        if on this map.
        """
        tilesize = (tile[2] - tile[0], tile[3] - tile[1])
        heightmap = self.zone.getHeightmapRegion(tile)
       
        minpt = self.zone.IToR(tile[0:2])
        maxpt = self.zone.IToR(tile[2:4])

        layerlist = self.layers.keys();
        layerlist.sort()
        for layer in layerlist:
            if self.zone.greyscale:
                image = Image.new('L', tilesize, 0)
            else:
                image = Image.new('RGBA', tilesize, (0,0,0,0))

            draw = ImageDraw.ImageDraw(image)

            for zkey, x, y, z, a, mag, nif in self.layers[layer]:
                r = nif.radius * mag / 100
                if (x + r) < minpt[0] or (x - r) > maxpt[0] or (y + r) < minpt[1] or (y - r) > maxpt[1]:
                    continue  # not on this tile.

                # Post river render: check for fixtures that stick out of the water.
                if self.zone.riverdone:
                    SCALEFACTOR = tilesize[0] / 65536.0
                    map_pt = ((x-minpt[0])*SCALEFACTOR,(y-minpt[1])*SCALEFACTOR)
                        # fix-up any bad map coords
                    if map_pt[0] < 0:
                        map_pt = (0,map_pt[1])
                    if map_pt[0] >= tilesize[0]:
                        map_pt = (tilesize[0]-1,map_pt[1])
                    if map_pt[1] < 0:
                        map_pt = (map_pt[0],0)
                    if map_pt[1] >= tilesize[1]:
                        map_pt = (map_pt[0],tilesize[1]-1)
                            
                        # get terrain height for the map_pts.
                    try:
                        map_z = heightmap.getpixel(map_pt) - self.minheight
                    except IndexError:
                        print 'x,y = (%d,%d) map_pt = (%d,%d); minpt=(%d,%d); maxpt=(%d,%d)' \
                              % (x,y,map_pt[0],map_pt[1],
                                 minpt[0],minpt[1],maxpt[0],maxpt[1])
                        
                    # Use the highest point of terrain    
                    terr_z = max(map_z,z)
                    
                    if (terr_z + nif.maxz * mag / 100) < min(self.zone.riverheight):
##                         print 'skipping underwater NIF %d,%d,%d' % (x,y,z)
                        continue
                    else:
                        pass
##                         print 'rendering NIF %d,%d,%d' % (x,y,z)
##                         print 'terr_z,z,nif.maxz,riverheight,minheight = (%d,%d,%d,%d,%d)' \
##                              % (terr_z,z,nif.maxz,min(self.zone.riverheight),self.minheight)
                nif.draw(self.zone, draw, x - minpt[0], y - minpt[1], a, mag)
            
            if self.zone.greyscale:
                destimage.paste(0, tile, image)
            else:
                destimage.paste(image, tile, image)

# Change History:
# 
# $Log: FixtureRender.py,v $
# Revision 1.16  2004/08/11 16:07:36  cyhiggin
# sync with mapper-base
#
# Revision 1.15  2004/08/11 16:06:14  cyhiggin
# Removed bounding box check of heights, as unnecessary and adds extra calculations.
#
# Revision 1.14  2004/08/09 01:59:11  cyhiggin
# Put check for abovewater fixtures back in.
#
# Revision 1.13  2004/08/08 21:46:03  cyhiggin
# removed check for above-water structures, and diagnostics prints
#
# Revision 1.12  2004/08/06 21:39:39  cyhiggin
# revised water-line height check
#
# Revision 1.11  2004/08/05 17:24:04  cyhiggin
# Added code to handle bad/missing tree NIFs. If tree is missing, substitute a default tree instead.
#
# Revision 1.10  2004/08/04 21:10:51  cyhiggin
# Commented out some diagnostic prints.
#
# Revision 1.9  2004/08/02 04:24:34  cyhiggin
# Started adding proper docstrings
# Added check for fixtures at waterline, in 2nd pass after rivers rendered.
#
# Revision 1.8  2004/05/27 14:04:04  cyhiggin
# Added GroveRender, renderer for tree clusters/groves to mapper.
#
# Revision 1.7  2004/05/13 02:08:26  cyhiggin
# Added frontiers/nifs to search path for NIFS.
#
# Revision 1.6  2004/04/03 16:18:58  cyhiggin
# Look for NPKs in yet more directories, like Trees/ and phousing/nifs/.
#
# Revision 1.5  2004/04/01 21:43:26  cyhiggin
# Added check for uppercase filename when searching for NPK..
#
# Revision 1.4  2004/04/01 17:52:24  cyhiggin
# Merged NIF4 and path adjustments from Calien into mapper codebase
#
# Revision 1.3  2004/03/14 23:25:51  cyhiggin
# fixtures settings improperly looking for light-vector instead of
# light-vect, fixed. More trying to find the right path.
#
# Revision 1.2  2004/03/14 21:24:15  cyhiggin
# corrected ReadPoly() to handle mixed case names
#
# 24/3/2002 G. Willoughby <sab@freeuk.com>
# line 231: changed 'print' to 'sys.stdout.write' and added a '\n' to the end

