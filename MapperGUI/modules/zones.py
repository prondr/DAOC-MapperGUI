# MapperGUI: a GUI for 'Oliver Jowett's DAoC mapper.py'
# See http://www.randomly.org/projects/mapper/
# 	$Id: zones.py,v 1.3 2004/04/16 16:38:16 cyhiggin Exp $	

# Oliver Jowett's DAoC mapper is included with this release because minor modifications were
# done to it to facilitate a GUI. See relevant files for change history.

# Copyright (c) 2002, G. Willoughby <sab@freeuk.com>
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
sys.path.append("../mapper")
import dempak
import datParser as ConfigParser

class Zones:
	def __init__(self, gamepath):
		try:
			self.locations=[]
			cp=ConfigParser.ConfigParser()
			cp.readfp(dempak.getMPAKEntry(os.path.join(gamepath, 'zones', 'zones.mpk'), 'zones.dat'))
			sections=cp.sections()
			sections.sort()

			for s in sections:
				if s[:4] == 'zone':
					id=int(s[4:])
					enabled=int(cp.get(s, 'enabled'))
					name=cp.get(s, 'name')
					region=cp.get(s,'region'); # need region to id realm -- cch
					try:
						type=int(cp.get(s, 'type'))
					except ConfigParser.NoOptionError:
						type=0
					if type==0 or type==3:
						# add region to tuple -- cch
						self.locations.append(("%03d" % id, name, region))
					else:   # ignore type 1,2,4 (city,dungeon,TOA city)
						continue

			dataFile=open("mapper/all_locations.txt","w")
			for x in range(len(self.locations)):
				dataFile.write("%s : %s\n" % (self.locations[x][0], self.locations[x][1]))
			dataFile.close()

		except IOError:
			self.locations=None


# ChangeLog
# $Log: zones.py,v $
# Revision 1.3  2004/04/16 16:38:16  cyhiggin
# Added region to zones tuple.
#
# Revision 1.2  2004/03/15 21:51:51  cyhiggin
# Changed Zones.__init__ to only list type 1 & 3 zones.
#
