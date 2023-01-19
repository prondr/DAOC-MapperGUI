# $Id: GroveRender.py,v 1.6 2004/08/11 16:07:36 cyhiggin Exp $
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
import NIFToPoly, Tiler, dempak, Util, FixtureRender

class GroveShadedNIF(FixtureRender.ShadedNIF):
    def __init__(self, color, polylist, layer, lv, lmin, lmax, treecoords):
        FixtureRender.ShadedNIF.__init__(self, color, polylist, layer, lv, lmin, lmax)
        self.tree_coords = treecoords;

    def draw(self, zone, canvas, ox, oy, a, mag):
        for tree_offset in self.tree_coords:
            tx, ty, tz, tseed = tree_offset
            FixtureRender.ShadedNIF.draw(self, zone, canvas, ox+int(float(tx)),
                                         oy+int(float(ty)), a, mag)

class GrovePolyNIF(FixtureRender.PolyNIF):
    def __init__(self, outline, fill, polylist, layer, treecoords):
        FixtureRender.PolyNIF.__init__(self, outline, fill, polylist, layer)
        self.tree_coords = treecoords;

    def draw(self, zone, canvas, ox, oy, a, mag):
        for tree_offset in self.tree_coords:
            tx, ty, tz, tseed = tree_offset
            FixtureRender.PolyNIF.draw(self, zone, canvas, ox+int(float(tx)),
                                       oy+int(float(ty)), a, mag)

                  
class MissingMPK:
    def __init__(self, file):
        self.file = file
        self.layer = 1
        self.warned = 0
        self.radius = 0
        self.maxz = 0
    
    def draw(self, zone, canvas, ox, oy, a, mag):
        if not self.warned:
            print "warning: use of missing grove MPK " + self.file
            self.warned = 1

def findtheMPKfile(zone, file):
    """ find the MPK file containing cluster (grove) data for file """
    
    speelings = [file, file.capitalize(), file.upper()]
    for myfname in speelings:

        # First, we try Trees, because that's where groves first appeared.
        # note that these are MPKs, not NPKs.
        nifdir = os.path.join(zone.gamepath, 'zones', 'Trees', 'clusters')
        npkpath = os.path.join(nifdir, myfname + '.mpk')
        if os.path.exists(npkpath):
            break;

         # try not capitalized...
        if not os.path.exists(nifdir):
            nifdir = os.path.join(zone.gamepath, 'zones', 'trees', 'clusters')
        # now test with file name
        npkpath = os.path.join(nifdir, myfname + '.mpk')
        # we found it?
        if os.path.exists(npkpath):
            break
    return npkpath

    
#
# Renderer
#

class GroveRender(Tiler.Tiler):
    def __init__(self, zone, name):
        Tiler.Tiler.__init__(self, zone, name)

    _re_GroveNIF = re.compile(r'([^.,]+)\.nif', re.IGNORECASE)
    _re_treeclusterNIF = re.compile(r'([^.,]+)\.nif,([^.,]+)\.nif,', re.IGNORECASE)
    _re_TreeTuple = re.compile(r'(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.\d+),(\d+),?')
    _grovecache = []

    def checkTreeClustersFile(self, zone, file):
        """ Open the tree_clusters.csv file and get grove info from it. """
    
        niffile = None
        self.tree_coords = []
        if not len(GroveRender._grovecache):
            clfile = os.path.join(zone.gamepath, 'zones', 'Trees', 'tree_clusters.mpk')
            if not os.path.exists(clfile):
                return False
            mpk = dempak.MPAKFile(clfile)
            csvfile = mpk.open('tree_clusters.csv')
            GroveRender._grovecache = csvfile.readlines()       # read in the whole file
            del GroveRender._grovecache[0]                      # toss the first line
            csvfile.close()
            mpk.close()
            
        for a in GroveRender._grovecache:
            m = GroveRender._re_treeclusterNIF.match(a)
            if m and m.group(1) == file:
                niffile = m.group(2)
                self.tree_coords = GroveRender._re_TreeTuple.findall(a)
                break
            
        return niffile
    
    def readGroveDefinition(self, file):
        niffile = None
        self.tree_coords = []
        mpk = dempak.MPAKFile(file)
        csvfile = os.path.basename(file)
        csvfile, ext = os.path.splitext(csvfile)
        datafile = mpk.open(csvfile + '.csv')
        l = datafile.readline()  # toss first line
        l = datafile.readline()
        match = GroveRender._re_GroveNIF.match(l);
        if match:
            niffile = match.group(1)
            self.tree_coords = GroveRender._re_TreeTuple.findall(l)
        else:
            print "Couldn't read NIF name in %s: %s" % (csvfile+'.csv', l)
            
        datafile.close()
        mpk.close()
        return niffile

    def preRender(self):
        self.readNIFs()
        self.readFixtures() 


    _re_NIF = re.compile(r'(\d+),[^,]+,([^,]+)\.(nif),\d+,\d+,(\d+),.*', re.IGNORECASE)
    def readNIFs(self):
        try: classify = self.zone.settings.get(self.name, 'classify')
        except ConfigParser.NoOptionError: classify = None
        
        self.nifmap = {}
        nifs = self.zone.datafile('nifs.csv')
        for l in nifs.readlines():
            match = GroveRender._re_NIF.match(l)
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

                # Locate the right .mpk
                # search treeclusters first.
                niffile = self.checkTreeClustersFile(self.zone,file)
                if not niffile:
                    mpkpath = findtheMPKfile(self.zone,file)
                    if not os.path.exists(mpkpath):
                        self.nifmap[id] = MissingMPK(file);
                        continue;
                    # read the grove definition.
                    niffile = self.readGroveDefinition(mpkpath)
                    
                polylist = FixtureRender.readPolys(self.zone, niffile)
                if polylist:
                    if type == 'wireframe':
                        color = self.zone.getColor(variant, 'color', default)
                        self.nifmap[id] = GrovePolyNIF(color, None, polylist,
                                                       layer, self.tree_coords)
                    elif type == 'solid':
                        o = self.zone.getColor(variant, 'outline', default)
                        f = self.zone.getColor(variant, 'fill', default)
                        self.nifmap[id] =  GrovePolyNIF(o, f, polylist,
                                                        layer, self.tree_coords)
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

                        self.nifmap[id] = GroveShadedNIF(color, polylist, layer, lv,
                                                         lmin, lmax, self.tree_coords)
                    else:
                        raise RuntimeError, 'unknown NIF type: ' + type
                else:
                    self.nifmap[id] = FixtureRender.MissingNIF(file)

        nifs.close()


    _re_Fixture = re.compile(r'\d+,(\d+),[^,]+,(\d+),(\d+),\d+,(\d+),(\d+),.*')
    def readFixtures(self):
        self.layers = {}
        fixtures = self.zone.datafile('fixtures.csv')
        for l in fixtures.readlines():
            match = GroveRender._re_Fixture.match(l)
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
                a = int(match.group(4))
                mag = int(match.group(5))

                zkey = nif.maxz * a
                data = (zkey,x,y,a,mag,nif)

                if self.layers.has_key(nif.layer):
                    self.layers[nif.layer].append(data)
                else:
                    self.layers[nif.layer] = [data]

        fixtures.close()

        layers = self.layers.keys();
        layers.sort()
        for layer in layers:
            self.layers[layer].sort()

    # Temporary images needed:
    #   greyscale: 3xL(tilesize)
    #   colour:    2xRGB(tilesize) + 1xRGBA(tilesize)
    def renderTile(self, destimage, tile):
        tilesize = (tile[2] - tile[0], tile[3] - tile[1])
        
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

            for zkey, x, y, a, mag, nif in self.layers[layer]:
                r = nif.radius * mag / 100
                if (x + r) < minpt[0] or (x - r) > maxpt[0] or (y + r) < minpt[1] or (y - r) > maxpt[1]:
                    continue  # not on this tile.
            
                nif.draw(self.zone, draw, x - minpt[0], y - minpt[1], a, mag)
            
            if self.zone.greyscale:
                destimage.paste(0, tile, image)
            else:
                destimage.paste(image, tile, image)


# Change History:
# 
# $Log: GroveRender.py,v $
# Revision 1.6  2004/08/11 16:07:36  cyhiggin
# sync with mapper-base
#
# Revision 1.2  2004/05/27 19:40:17  cyhiggin
# Added new function to check new tree_clusters.csv
#
# Revision 1.1  2004/05/27 14:04:04  cyhiggin
# Added GroveRender, renderer for tree clusters/groves to mapper.
#

