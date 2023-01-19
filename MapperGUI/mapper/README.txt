DAoC mapper - 2002/02/10
Oliver Jowett <oliver@randomly.org>

See http://www.randomly.org/projects/mapper/ for more information and updates.

---

I know, this documentation sucks. I hate writing documentation. Something
better will turn up eventually..

---

Contents of this package:

  README.txt:       This file; pretends to be documentation.

  zonelist.py:      zone listing script

  mapper.py:        main mapping script
     *Render.py:    renderer modules for the mapper
     Tiler.py:      mapper utility module
     Util.py:       mapper utility module
     Zone.py:       mapper utility module

  default.ini:      sample mapper configuration file
     local.ini:     local part of configuration file
     locations.ini: defines locations to render via -location
     captions.ini:  defines captions used by the caption renderer

  everything.ini:   settings I use to render the maps on my website
  overview.ini:     settings I use to render the maps on my website
                    (this one is used to generate the maps that make up the
                     small composite overview maps used as imagemaps)

  dempak.py:        .mpk/.npk extractor: used by mapper.py, also runs 
                       standalone.
  NIFToPoly.py:     .nif extractor: used by mapper.py, also runs standalone.

  *.pil, *.pbm:     sample fonts, see the website for where to get more.

---

Quick usage guide:

Take a look at default.ini to see how things are configured; the idea is to
have a .ini for each rendering style you want to use. default.ini 
automatically includes the settings in local.ini, locations.ini, and
captions.ini. You'll need to change local.ini for your installation
(specifically, set gamepath to point to your client install)

To run: python mapper.py options...

Options are:

  -settings <ini-file-name>: read a settings file; this is where renderers
     are configured. This can be specified more than once to read several
     files. Required.

  -scale <size>: set image size to <size>x<size>. Note that this is the actual
     output size only if you are rendering a complete zone; if you use
     -region or -location as well, the image will be smaller. Defaults to 512.

  -out <outfile>: set the output filename. Required.

  -zone <zoneID>: set the zone number to render. Either this or -location is
     required.

  -region <x1> <y1> <x2> <y2>: render only part of a zone. x and y values
     are 0..65536 (independent of image scale). Defaults to rendering the
     entire zone.

  -renderers <renderer-list>: override the 'renderers' option in [maps] in
     the .ini files; useful for a one-off rendering

  -location <name>: render a preset location, based on a name that corresponds
     to a name in the [locations] .ini section. See locations.ini for a couple
     of examples. This overrides both -region and -zoneID.

  -gamepath <path>: set game path; overrides the gamepath option in [maps]

  -polydir <path>: set polygon data dir; overrides the polydir option in [maps]

---

See comments in default.ini and comments in each of the renderer source files
for details on the individual renderer options.

---

Suggestions, success stories, bugs, etc. are welcome.

Oliver Jowett <oliver@randomly.org>
