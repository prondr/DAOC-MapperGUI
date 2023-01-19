# $Id: Util.py,v 1.6 2004/08/11 16:07:36 cyhiggin Exp $
# Util.py: DAoC mapper, misc. helper code
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

import Image, math

def Scale256(zone, source, region):
    """
    Scale a 256x256 imagemap to region-size
    
    Extract a smoothly scaled section of 'source' (a 256x256 image presumed to
    "cover" the entire zone) corresponding to image coordinates 'region'. This
    is used to extract parts of the heightmap and lightmap.
    """
    bounds = [int(zone.IToRX(region[0]) / 256.0 + 0.5) - 1,
              int(zone.IToRY(region[1]) / 256.0 + 0.5) - 1,
              int(zone.IToRX(region[2]) / 256.0 + 0.5) + 1,
              int(zone.IToRY(region[3]) / 256.0 + 0.5) + 1]
    
    if bounds[0] < 0: bounds[0] = 0
    if bounds[1] < 0: bounds[1] = 0
    if bounds[2] > 256: bounds[2] = 256
    if bounds[3] > 256: bounds[3] = 256

    # find image of region within scaled image that we want
    scaled_bounds = (region[0] - zone.RToIX(bounds[0] * 256),
                     region[1] - zone.RToIY(bounds[1] * 256),
                     region[2] - zone.RToIX(bounds[0] * 256),
                     region[3] - zone.RToIY(bounds[1] * 256))
    
    resize_to = ( zone.RToIScale(256 * (bounds[2] - bounds[0])),
                  zone.RToIScale(256 * (bounds[3] - bounds[1])) )

    #print "region=", region, "source-bounds=", bounds, "resize_to=", resize_to, "scaled-bounds=", scaled_bounds

    i1 = source.crop(bounds)
    i2 = i1.resize(resize_to, Image.BILINEAR)
    del i1
    i3 = i2.crop(scaled_bounds)
    del i2
    return i3

def crossprod(p1, p2):
    """Calculate p1 X p2 where p1,p2 are 3x1 vectors
    """
    # i   j   k
    # p1x p1y p1z
    # p2x p2y p2z

    return ( p1[1]*p2[2] - p1[2]*p2[1],
             -(p1[0]*p2[2] - p1[2]*p2[0]),
             p1[0]*p2[1] - p1[1]*p2[0] )

def normal(p1, p2, p3):
    """Calculate a normal vector (not normalized) to the triangle p1,p2,p3
    """
    v1 = (p2[0] - p1[0],
          p2[1] - p1[1],
          p2[2] - p1[2])
    v2 = (p3[0] - p2[0],
          p3[1] - p2[1],
          p3[2] - p2[2])
    return crossprod(v1, v2)

def normalize(v):
    """Normalize a 3x1 vector
    """
    modulus = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if modulus == 0 : 
      modulus = 1e-50
      #print "warning"
    return (v[0]/modulus, v[1]/modulus, v[2]/modulus)

# Change Log
#
# $Log: Util.py,v $
# Revision 1.6  2004/08/11 16:07:36  cyhiggin
# sync with mapper-base
#
# Revision 1.4  2004/07/31 22:42:19  cyhiggin
# More of same.
#
# Revision 1.3  2004/07/31 22:41:25  cyhiggin
# Started adding proper docstrings.
#
