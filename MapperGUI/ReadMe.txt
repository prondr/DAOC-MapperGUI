MapperGUI (Win32): a GUI for 'Oliver Jowett's DAoC mapper.py'

FYI: Oliver Jowett's DAoC mapper is included with this release because minor modifications were done to it to facilitate a GUI. See relevant files for change history.

===================================================================================================================

Game description:
Dark Age of Camelot is a massively multi-player online role-playing game conceived and developed by Mythic Entertainment. Set in the Kingdom of Albion in the years immediately following the death of King Arthur, players of the game enter a world in chaos, where Arthur’s peace has been shattered and dark forces threaten the Kingdom. 

Program Summary:
DAoC MapperGUI is a graphical user interface to 'Oliver Jowett's DAoC mapper.py', a Dark Age of Camelot mapping program written entirely in Python <www.python.org>. The core mapper program written by Oliver Jowett scans the game files installed on your drive and dynamically renders an image. The core files can be found here: <www.randomly.org> I have made minor adjustments to Oliver Jowett's code to facilitate a GUI, so the modified core program is included with the GUI download.

Features:
Handy sliders to control light and transparency
Simple checkboxes to switch map features on or off
Simple colour selectors for different colour schemes
Region mapping: Render a full zone then draw a marquee around a region then hit 'Render' again!
Outlined coloured captions
Integrated caption editor
Variable image size

Why Python?:
Because its cool to be seen to use a cool programming language! ...(and C++ muddles my brain!)

Why MapperGUI?
Because nice maps are hard to find for this game and I keep getting lost damnit!  :)

Installation:

1). Install Activstate python v2.1+ and remember the folder you installed to.
2). Restart you PC
3). Install PIL (python imaging library) and install into the python folder (you can use the python package manager (double click on pyppm.py while connected to the net) to install PIL (python imaging library), when the PPM comes up type 'install PIL' and it will do its magic then type 'exit' when it has finished)
4). Restart you PC again.
5). All done!  :)

Troubleshooting:
Some people have had a problem where the render box momentarily pops up then dissapears without rendering a map, this is easily solved by putting your python install path in your 'autoexec.bat' file. (Why the Activestate installer forgets to do this i'll never know!) Open your 'autoexec.bat' file with a text editor such as 'notepad.exe' In this file there is an entry begining with 'PATH' it looks something like this:
SET PATH="C:\WINDOWS;C:\WINDOWS\SYSTEM;C:\WINDOWS\COMMAND;C:\PROGRA~1\PY THON;C:\PROGRA~1\PYTHON\LIB;C:\PROGRA~1\PYTHON\PIL ;C:WINDOWS\PROGRA~1\PYTHON\DLLs
notice the 'C:\PROGRA~1\PYTHON' entry, this is where i have python installed! you should make sure where ever your python installation is it should be listed here. also notice all paths are seperated by semi-colons (;) save this file and restart! NOTE: if you are using Win2000 the path is accessed here:
Control Panel/System/Advanced/Environment Variables/Systemvariables/Path

Activestate Python v2.1+:
<http://www.activestate.com/Products/ActivePython>

PIL (python imaging library):
<http://www.pythonware.com/products/pil/>

If you have python installed but its not the Activestate version and you are having problems you may need to install the
windows specific Win32all module too:
<http://aspn.activestate.com/ASPN/Downloads/ActivePython/Extensions/Win32all>.

Contact:
Praise, Bugs, Grief, whatever, please send to sab@freeuk.com

History:
v1.0
Initial Release
v1.1
Fixed menu not displaying 'Vale of Mularn' and 'Lough Derg'.
Added new menu cascade regarding Misc/Unknown locations!
Added extra module info to readme regarding Win32all extensions.  sorry!  :)
v1.2
Fixed gamepath (you can now have spaces in your gamepath.)
v1.3
Image size has now got to be below 2000 pixels wide (for some reason the core (Tcl/Tk) crashes badly above 2000.)
v1.4
Beta release
v1.5
Fixed a bug regarding the v1.49 patch (Mythic had forgoten to comment out some text in one of their '.dat' files, tut, tut..  :)
Added 'OneClick' captioning
Added new features to the caption editor
v1.6
A few optimisation tweaks
'Realtime' updating of the map!
Because of an update to the Python v2+ release, win32pipe.popen() is no longer needed, os.popen() will do.
This should negate the need for the Win32all package being installed  :)
Fixed a bug populating the caption editor with the wrong coords from the map if the image size was over 564 pixels.  ooops!  :(

===================================================================================================================

MapperGUI:
Copyright (c) 2002, G. Willoughby <sab@freeuk.com> All rights reserved.

Dark Age of Camelot:
Copyright (c) 2001, Mythic Entertainment, Inc. All rights reserved. Mythic Entertainment, the Mythic Entertainment logo, "Dark Age of Camelot", the Dark Age of Camelot logo, stylized Celtic knot and "Live the Legend" are trademarks of Mythic Entertainment, Inc. Abandon Entertainment and the Abandon Entertainment logo are trademarks of Abandon Entertainment, Inc.