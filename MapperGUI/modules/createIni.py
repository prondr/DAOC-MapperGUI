# $Id: createIni.py,v 1.14 2004/08/17 13:29:55 cyhiggin Exp $
# MapperGUI: a GUI for 'Oliver Jowett's DAoC mapper.py'
# See http://www.randomly.org/projects/mapper/

# Oliver Jowett's DAoC mapper is included with this release because
# minor modifications were
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

class CreateMapperINI:
    """Creates mappergui.ini settings file.
    """
    def __init__(self, *args):
        
        INIFile=open("mapper/mappergui.ini", "w")

        # write header
        INIFile.write("; DO NOT MODIFY THIS FILE!\n")
        INIFile.write("; Dynamically generated from MapperGUI.py\n")
        INIFile.write("\n")
        
        INIFile.write("[maps]\n")
        INIFile.write("mode=color\n")        
        if args[0][30]=="1":
            INIFile.write("byline = %s\n" % args[0][31])
            INIFile.write("bylinefont = 6x12-ISO8859-1.pil\n")
        if args[0][26]=="1":
            INIFile.write("include=captions.ini,local.ini\n")
        else:
            INIFile.write("include=local.ini\n")
        INIFile.write("\n")

        # write renderers
        renderers=[]
        if args[0][0]=="1":
            renderers.append("background")
        if args[0][4]=="1":
            renderers.append("bumpmap")
        if args[0][7]=="1":
            renderers.append("contours")
        if args[0][14]=="1":
            renderers.append("huglydecor")
            renderers.append("structures")
        if args[0][9]=="1":
            renderers.append("grove")
            renderers.append("trees")
        if args[0][1]=="1":
            renderers.append("river")
            # 2nd structure render after river, to catch waterline structures.
            if args[0][1]=="1":
                renderers.append("structures")
        if args[0][19]=="1":
            renderers.append("bounds")
        if args[0][22]=="1":
            renderers.append("grid")
        if args[0][24]=="1":
            renderers.append("grid2")
        if args[0][26]=="1":
            renderers.append("captions")
        INIFile.write("renderers=")
        for x in range(len(renderers)):
            if x<len(renderers)-1:
                INIFile.write("%s, " % renderers[x])
            elif x==len(renderers)-1:
                INIFile.write("%s\n " % renderers[x])
        INIFile.write("\n")
        
        # write background
        INIFile.write("[background]\n")
        INIFile.write("type=background\n")
        INIFile.write("\n")

        # write boundries
        INIFile.write("[bounds]\n")
        INIFile.write("type=bounds\n")
        INIFile.write("alpha=%s\n" % args[0][21])
        INIFile.write("color=%s\n" % args[0][20])
        INIFile.write("fill=%s\n" % args[0][29])
        INIFile.write("\n")

        # write outer grid
        INIFile.write("[grid]\n")
        INIFile.write("type=grid\n")
        INIFile.write("interval=10000\n")
        INIFile.write("color=0,0,0\n")
        INIFile.write("alpha=%s\n" % args[0][23])
        INIFile.write("font=6x12-ISO8859-1.pil\n")
        INIFile.write("fontcolor=0,0,0\n")
        INIFile.write("\n")
    
        # write inner grid
        INIFile.write("[grid2]\n")
        INIFile.write("type=grid\n")
        INIFile.write("interval=1000\n")
        INIFile.write("color=0,0,0\n")
        INIFile.write("alpha=%s\n" % args[0][25])
        INIFile.write("\n")
        
        # write captions
        INIFile.write("[captions]\n")
        INIFile.write("type=caption\n")
        INIFile.write("source=town-captions\n")
        INIFile.write("font=6x12-ISO8859-1.pil\n")
        INIFile.write(";font=timR24-ISO8859-1.pil\n")
        INIFile.write("color=%s\n" % args[0][27])
        INIFile.write("\n")
        
        # write contours
        INIFile.write("[contours]\n")
        INIFile.write("type=contour\n")
        INIFile.write("interval=%s\n" % args[0][8])
        INIFile.write("\n")
        
        # write river
        INIFile.write("[river]\n")
        INIFile.write("type=river\n")
        INIFile.write("alpha=%s\n" % args[0][3])
        INIFile.write("color=%s\n" % args[0][2])
        INIFile.write("\n")
        
        # write bumpmap
        INIFile.write("[bumpmap]\n")
        INIFile.write("type=bumpmap\n")
        INIFile.write("z_scale=20.0\n")
        INIFile.write("light_vect=-1.0,1.0,-1.0\n")
        args[0][5]=float(args[0][5])/10
        INIFile.write("light_min=%s\n" % args[0][5])
        args[0][6]=float(args[0][6])/10
        INIFile.write("light_max=%s\n" % args[0][6])
        INIFile.write("\n")
        
        # write trees
        INIFile.write("[trees]\n")
        INIFile.write("type=fixture\n")
        INIFile.write("classify=fixture-classes\n")
        INIFile.write("default=draw.none\n")
        INIFile.write("tree=draw.tree\n")
        INIFile.write("\n")
        
        # write huglydecor
        INIFile.write("[huglydecor]\n")
        INIFile.write("type = fixture\n")
        INIFile.write("classify = fixture-classes\n")
        INIFile.write("default = draw.none\n")
        INIFile.write("decor = draw.decor\n")
        INIFile.write("\n")
        
        # write grove
        INIFile.write("[grove]\n")
        INIFile.write("type = grove\n")
        INIFile.write("classify = fixture-classes\n")
        INIFile.write("default = draw.none\n")
        INIFile.write("grove = draw.tree\n")
        INIFile.write("\n")
        
        # write structures
        INIFile.write("[structures]\n")
        INIFile.write("type=fixture\n")
        INIFile.write("classify=fixture-classes\n")
        INIFile.write("default=draw.shaded\n")
        INIFile.write("tree=draw.none\n")
        INIFile.write("erreur=draw.none\n")
        INIFile.write("collidee=draw.none\n")
        INIFile.write("decor=draw.none\n")
        INIFile.write("grove=draw.none\n")
        INIFile.write("\n")

        # trees continued...
        INIFile.write("[draw.tree]\n")
        INIFile.write("type=shaded\n")
        INIFile.write("light_vect=-1.0,1.0,-1.0\n")
        args[0][12]=float(args[0][12])/10
        INIFile.write("light_min=%s\n" % args[0][12])
        args[0][13]=float(args[0][13])/10
        INIFile.write("light_max=%s\n" % args[0][13])
        INIFile.write("color=%s,%s\n" % (args[0][10], args[0][11]))
        INIFile.write("layer=0\n")
        INIFile.write("defaulttree=Elm1\n")
        INIFile.write("\n")
        
        # structures continued...
        INIFile.write("[draw.shaded]\n")
        INIFile.write("type=shaded\n")
        INIFile.write("light_vect=-1.0,1.0,-1.0\n")
        args[0][17]=float(args[0][17])/10
        INIFile.write("light_min=%s\n" % args[0][17])
        args[0][18]=float(args[0][18])/10
        INIFile.write("light_max=%s\n" % args[0][18])
        INIFile.write("color=%s,%s\n" % (args[0][15], args[0][16]))
        INIFile.write("layer=1\n")
        INIFile.write("\n")
        
        # decor
        INIFile.write("[draw.decor]\n")
## 		INIFile.write("type=solid\n")
        INIFile.write("type=shaded\n")
        INIFile.write("light_vect = -1.0,1.0,-1.0\n")
        # for now, use same settings as structures.
        # May add new setting later.
        INIFile.write("light_min=%s\n" % args[0][17])
        INIFile.write("light_max=%s\n" % args[0][18])
        INIFile.write("color=%s,%s\n" % (args[0][15], args[0][16]))
## 		INIFile.write("color=default\n")
## 		INIFile.write("fill=default\n")
## 		INIFile.write("outline=default\n")
        
        INIFile.write("layer=1\n")
        INIFile.write("\n")
        
        # Misc
        INIFile.write("[draw.none]\n")
        INIFile.write("type=none\n")
        INIFile.write("\n")
        
        INIFile.write("[fixture-classes]\n")
        INIFile.write("; new atlantis stuff\n")
        INIFile.write("; new frontiers groves\n")
        INIFile.write("aegcliffpiece1 = decor\n")
        INIFile.write("aegcliffpiece2 = decor\n")
        INIFile.write("aegcliffpiece3 = decor\n")
        INIFile.write("aegcliffpiece4 = decor\n")
        INIFile.write("aegcliffpiece5 = decor\n")
        INIFile.write("aegcliffpiece6 = decor\n")
        INIFile.write("aegcliffpiece7 = decor\n")
        INIFile.write("aegcliffpiece8 = decor\n")
        INIFile.write("aegcliffwalls = decor\n")
        INIFile.write("aeris_oak=tree\n")
        INIFile.write("aerus_fallen_tree1=tree\n")
        INIFile.write("aerus_fallen_tree2=tree\n")
        INIFile.write("aerus_fallen_tree3=tree\n")
        INIFile.write("aerus_fallen_tree4=tree\n")
        INIFile.write("aerus_fallen_tree5=tree\n")
        INIFile.write("alder = tree\n")
        INIFile.write("amurcork=tree\n")
        INIFile.write("appletree = tree\n")
        INIFile.write("ash = tree\n")
        INIFile.write("b_bush1 = tree\n")
        INIFile.write("b_htoak1 = tree\n")
        INIFile.write("b_htoakb = tree\n")
        INIFile.write("baretree = tree\n")
        INIFile.write("bbare1 = tree\n")
        INIFile.write("bbare2 = tree\n")
        INIFile.write("beech = tree\n")
        INIFile.write("beech_gnarl = tree\n")
        INIFile.write("beech_gnarl_dead = tree\n")
        INIFile.write("bighibtree = tree\n")
        INIFile.write("bigpalm = tree\n")
        INIFile.write("bigtree = tree\n")
        INIFile.write("blackgum = tree\n")
        INIFile.write("blackgum_rt = tree\n")
        INIFile.write("bluefir = tree\n")
        INIFile.write("bmtntre1 = tree\n")
        INIFile.write("bpinea = tree\n")
        INIFile.write("bpineacl3 = grove\n")
        INIFile.write("bpinetree = tree\n")
        INIFile.write("browntree = tree\n")
        INIFile.write("brownwillow = tree\n")
        INIFile.write("brtstmp2 = tree\n")
        INIFile.write("brushclump = tree\n")
        INIFile.write("brushes = tree\n")
        INIFile.write("bspanmoss = tree\n")
        INIFile.write("btaltre1 = tree\n")
        INIFile.write("burnt_tree = tree\n")
        INIFile.write("burnttree = tree\n")
        INIFile.write("burnt_liveoak = tree\n")
        INIFile.write("bvgrn1 = tree\n")
        INIFile.write("bvrgrn1 = tree\n")
        INIFile.write("bwillow = tree\n")
        INIFile.write("carolinabuckthorn = tree\n")
        INIFile.write("cedar = tree\n")
        INIFile.write("chestnut = tree\n")
        INIFile.write("coral_01 = tree\n")
        INIFile.write("coral_02 = tree\n")
        INIFile.write("coral_03 = tree\n")
        INIFile.write("coral_04 = tree\n")
        INIFile.write("cothpiece1 = decor\n")
        INIFile.write("cothpiece10 = decor\n")
        INIFile.write("cothpiece11 = decor\n")
        INIFile.write("cothpiece12 = decor\n")
        INIFile.write("cothpiece13 = decor\n")
        INIFile.write("cothpiece14 = decor\n")
        INIFile.write("cothpiece15 = decor\n")
        INIFile.write("cothpiece2 = decor\n")
        INIFile.write("cothpiece3 = decor\n")
        INIFile.write("cothpiece4 = decor\n")
        INIFile.write("cothpiece5 = decor\n")
        INIFile.write("cothpiece6 = decor\n")
        INIFile.write("cothpiece7 = decor\n")
        INIFile.write("cothpiece8 = decor\n")
        INIFile.write("cothpiece9 = decor\n")
        INIFile.write("creepywebpine = tree\n")
        INIFile.write("crookedpalm = tree\n")
        INIFile.write("darkamurcork = tree\n")
        INIFile.write("deadamurcork = tree\n")
        INIFile.write("delling01 = decor\n")
        INIFile.write("delling02 = decor\n")
        INIFile.write("delling03 = decor\n")
        INIFile.write("delling04 = decor\n")
        INIFile.write("delling05 = decor\n")
        INIFile.write("delling06 = decor\n")
        INIFile.write("delling07 = decor\n")
        INIFile.write("delling08 = decor\n")
        INIFile.write("delling09 = decor\n")
        INIFile.write("desert_bush = tree\n")
        INIFile.write("desert_bush2 = tree\n")
        INIFile.write("elm = tree\n")
        INIFile.write("elm1 = tree\n")
        INIFile.write("elm1cl5 = grove\n")
        INIFile.write("elm2 = tree\n")
        INIFile.write("elm2cl5 = grove\n")
        INIFile.write("englishoak = tree\n")
        INIFile.write("fallencreepytree = tree\n")
        INIFile.write("fern = tree\n")
        INIFile.write("fomorentrance1 = decor\n")
        INIFile.write("fomorentrance2 = decor\n")
        INIFile.write("fomorentrance3 = decor\n")
        INIFile.write("fomorentrance4 = decor\n")
        INIFile.write("gnarlamurcork = tree\n")
        INIFile.write("greenpine = tree\n")
        INIFile.write("gwydcliff1 = decor\n")
        INIFile.write("gwydcliff10 = decor\n")
        INIFile.write("gwydcliff11 = decor\n")
        INIFile.write("gwydcliff12 = decor\n")
        INIFile.write("gwydcliff13 = decor\n")
        INIFile.write("gwydcliff2 = decor\n")
        INIFile.write("gwydcliff3 = decor\n")
        INIFile.write("gwydcliff4 = decor\n")
        INIFile.write("gwydcliff5 = decor\n")
        INIFile.write("gwydcliff6 = decor\n")
        INIFile.write("gwydcliff7 = decor\n")
        INIFile.write("gwydcliff8 = decor\n")
        INIFile.write("gwydcliff9 = decor\n")
        INIFile.write("hbareskny = tree\n")
        INIFile.write("hbirchsingle = tree\n")
        INIFile.write("hbirchsinglecl5=grove\n")
        INIFile.write("hdeadtree = tree\n")
        INIFile.write("hdomtrashedtrees = tree\n")
        INIFile.write("helm = tree\n")
        INIFile.write("helm2 = tree\n")
        INIFile.write("hfirbtree = tree\n")
        INIFile.write("hiberniatall_whitepine3cl10 = grove\n")
        INIFile.write("hiberniatall_whitepine3cl10 = grove\n")
        INIFile.write("hiberniatall_whitepine3cl5 = grove\n")
        INIFile.write("hiberniatall_whitepine3cl5row = grove\n")
        INIFile.write("hiberniatall_whitepinecl10 = grove\n")
        INIFile.write("hiberniatall_whitepinecl5 = grove\n")
        INIFile.write("hlog = tree\n")
        INIFile.write("hlogbent = tree\n")
        INIFile.write("hlowtree = tree\n")
        INIFile.write("hlowtreecl5 = grove\n")
        INIFile.write("hlowtreecl5 = grove\n")
        INIFile.write("hoaktree = tree\n")
        INIFile.write("hoaktreecl5 = grove\n")
        INIFile.write("hol-stmp = tree\n")
        INIFile.write("holdgrove = tree\n")
        INIFile.write("hollytree = tree\n")
        INIFile.write("hollytreecl5 = grove\n")
        INIFile.write("hplant01 = tree\n")
        INIFile.write("hstumpy = tree\n")
        INIFile.write("hstumpyleaf = tree\n")
        INIFile.write("hweepwill = tree\n")
        INIFile.write("iarnwood = tree\n")
        INIFile.write("isspiece1 = decor\n")
        INIFile.write("isspiece2 = decor\n")
        INIFile.write("japanesemaple_rt_winter=tree\n")
        INIFile.write("kelpani=tree\n")
        INIFile.write("kelpgroup_red=tree\n")
        INIFile.write("kelpnon=tree\n")
        INIFile.write("lemontree=tree\n")
        INIFile.write("lillypads = tree\n")
        INIFile.write("lilypads = tree\n")
        INIFile.write("liveoak = tree\n")
        INIFile.write("log1 = tree\n")
        INIFile.write("log1-s = tree\n")
        INIFile.write("log2 = tree\n")
        INIFile.write("log2-s = tree\n")
        INIFile.write("maple = tree\n")
        INIFile.write("midgardtall_whitepine3cl10=grove\n")
        INIFile.write("midgardtall_whitepinecl10=grove\n")
        INIFile.write("mightyoak = tree\n")
        INIFile.write("mightyoak-small = tree\n")
        INIFile.write("n_stump = tree\n")
        INIFile.write("n_stump-s = tree\n")
        INIFile.write("nbirchtree = tree\n")
        INIFile.write("nbirchtreecl5=grove\n")
        INIFile.write("ncarcass = erreur\n")
        INIFile.write("npinea = tree\n")
        INIFile.write("npinea-s = tree\n")
        INIFile.write("npineacl5=grove\n")
        INIFile.write("npinedk = tree\n")
        INIFile.write("npinetree = tree\n")
        INIFile.write("npinetree-s = tree\n")
        INIFile.write("npinetree-scl5=grove\n")
        INIFile.write("npinetreecl5=grove\n")
        INIFile.write("npintre-s = tree\n")
        INIFile.write("npintre1 = tree\n")
        INIFile.write("npintre1-scl5=grove\n")
        INIFile.write("npintre1-scl5=grove\n")
        INIFile.write("npintre1cl5=grove\n")
        INIFile.write("npintree = tree\n")
        INIFile.write("nreeds = tree\n")
        INIFile.write("nrelickeep-s = collidee\n")
        INIFile.write("nrushes = tree\n")
        INIFile.write("nvrgrn1-s = tree\n")
        INIFile.write("nvrgrn1-scl5=grove\n")
        INIFile.write("nwereplatform = erreur\n")
        INIFile.write("oak1 = tree\n")
        INIFile.write("oak1a = tree\n")
        INIFile.write("ogrestrnghldquad1 = decor\n")
        INIFile.write("ogrestrnghldquad2 = decor\n")
        INIFile.write("ogrestrnghldquad3 = decor\n")
        INIFile.write("ogrestrnghldquad4 = decor\n")
        INIFile.write("olivetree = tree\n")
        INIFile.write("olivetree1 = tree\n")
        INIFile.write("paperbirchmulti = tree\n")
        INIFile.write("paperbirchsingle = tree\n")
        INIFile.write("pinetree = tree\n")
        INIFile.write("pintre1 = tree\n")
        INIFile.write("pintre1cl3 = grove\n")
        INIFile.write("redmaple = tree\n")
        INIFile.write("redwood_alive = tree\n")
        INIFile.write("redwood_dead = tree\n")
        INIFile.write("reeds = tree\n")
        INIFile.write("reedclump1 = tree\n")
        INIFile.write("skinnypalm = tree\n")
        INIFile.write("smallfir = tree\n")
        INIFile.write("smallgreenfir = tree\n")
        INIFile.write("smallpalm = tree\n")
        INIFile.write("smallsnowywhitepin = tree\n")
        INIFile.write("snowybluefir = tree\n")
        INIFile.write("snowyspruce = tree\n")
        INIFile.write("spruce = tree\n")
        INIFile.write("stonepine = tree\n")
        INIFile.write("tallbaretree = tree\n")
        INIFile.write("tallcedar = tree\n")
        INIFile.write("talloak = tree\n")
        INIFile.write("tall_whitepine1 = tree\n")
        INIFile.write("tall_whitepine2 = tree\n")
        INIFile.write("tall_whitepine2_snow = tree\n")
        INIFile.write("tall_whitepine3 = tree\n")
        INIFile.write("tall_whitepine4 = tree\n")
        INIFile.write("tall_whitepine5 = tree\n")
        INIFile.write("tall_whitepine = tree\n")
        INIFile.write("talloak1 = tree\n")
        INIFile.write("tulip = tree\n")
        INIFile.write("urchin_01 = tree\n")
        INIFile.write("vrgrn1 = tree\n")
        INIFile.write("vrgrn1cl5 = grove\n")
        INIFile.write("weepingwillow = tree\n")
        INIFile.write("willowcl3 = grove\n")
        INIFile.write("willowcl5 = grove\n")
        INIFile.write("willowoak = tree\n")
        INIFile.write("yellowtubes = tree\n")
        INIFile.write("yew = tree\n")
        INIFile.write("elm1cluster5 = grove\n")
        INIFile.write("elm2cluster5 = grove\n")
        INIFile.write("hlowtreecluster = grove\n")
        INIFile.write("tall_whitepine3cl10 = grove\n")
        INIFile.write("tall_whitepine3cluster = grove\n")
        INIFile.write("tall_whitepinecl10 = grove\n")
        INIFile.write("tall_whitepinecluster = grove\n")
        INIFile.close()

# $Log: createIni.py,v $
# Revision 1.14  2004/08/17 13:29:55  cyhiggin
# Added some more groves to ini-file generator.
#
# Revision 1.13  2004/08/05 20:30:07  cyhiggin
# Only adds byline entries if bylineOnOff (pref[30]) is on.
#
# Revision 1.12  2004/08/05 17:16:49  cyhiggin
# Added defaulttree entry to draw.trees
#
# Revision 1.11  2004/08/04 21:10:27  cyhiggin
# Added more Atlantean trees to list
#
# Revision 1.10  2004/08/04 20:04:48  cyhiggin
# Fixed indentation
#
# Revision 1.9  2004/08/04 19:55:16  cyhiggin
# fixed indent of docstring
#
# Revision 1.8  2004/08/04 19:52:05  cyhiggin
# Only add 2nd structure render if we render rivers.
#
# Revision 1.7  2004/08/02 02:39:55  cyhiggin
# Started adding proper docstrings
# Added 2nd structure render after rivers, to catch waterline structures.
#
# Revision 1.6  2004/07/28 21:22:03  cyhiggin
# Changed render order: rivers to render after structures, trees, groves.
#
# Revision 1.5  2004/05/28 13:59:52  cyhiggin
# bringing mapper-base mods into tree
#
# Revision 1.4  2004/04/16 23:02:08  cyhiggin
# Added new ini option to bounds: fill=0|1
#

