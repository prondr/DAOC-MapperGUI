"""MapperGUI: a GUI for 'Oliver Jowett's DAoC mapper.py'
"""
# See http://www.randomly.org/projects/mapper/
#     $Id: MapperGUI.pyw,v 1.15 2004/08/17 13:33:39 cyhiggin Exp $    

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

# From Python v2.3
from tkinter import *
import tkinter.filedialog, os, sys, string
sys.path.append("./modules")
sys.path.append("./mapper")
# From PIL
from PIL import Image, ImageTk
# From Modules
from helpViewer import HelpDialog
from tkinterAboutBox import AboutBox
import zones
from zones import Zones
from createIni import CreateMapperINI
from createLocalIni import CreateLocalINI
from captionEditor import EditorMain
import re

class GenericCallback:
    def __init__(self, callback, *firstArgs):
        self.__callback = callback
        self.__firstArgs = firstArgs
    def __call__(self, *lastArgs):
        self.__callback(*self.__firstArgs + lastArgs)

class LabelFrame(Frame):
    def __init__(self, master, labelText="Sample text", **kwargs):
        Frame.__init__(self, master, kwargs)
        self.label=Label(master, text=" %s " % labelText)
        self.label.place(in_=self, relx=0, rely=0, x=6, y=-11)

class RenderBox:
    """Rendering progress & messages window
    """
    def __init__(self, renderMaster="renderBox"):
        self.renderMaster=renderMaster
        self.renderMaster=Toplevel()
        self.renderMaster.withdraw()
        # make unclosable
        self.renderMaster.protocol('WM_DELETE_WINDOW', lambda:0)
        self.renderMaster.title("Rendering...")
        self.scrollbar = Scrollbar(self.renderMaster, orient=VERTICAL)
        self.logger=Listbox(self.renderMaster, bd=1, relief=SUNKEN, width=70, height=9, takefocus=0, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.logger.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.logger.pack(side=LEFT, fill=BOTH, expand=1)
        self.renderMaster.update_idletasks()
        # CCH -- winfo_width vs winfo_reqwidth
        self.renderMaster.geometry("%dx%d+%d+%d" % (self.renderMaster.winfo_reqwidth(), self.renderMaster.winfo_reqheight(), (self.renderMaster.winfo_screenwidth()/2)-(self.renderMaster.winfo_reqwidth()/2)-95, (self.renderMaster.winfo_screenheight()/2)-(self.renderMaster.winfo_reqheight()/2)-40))
        self.renderMaster.deiconify()
        self.renderMaster.focus_set()
        self.imageSize=app.imageSizeEntry.get()
        os.chdir("mapper")
        if app.rubberbandBox==None and app.batchRender==None:
            # CCH -- made python exec name a variable.
            self.mapperScriptOutput=os.popen("%s mapper.py -settings mappergui.ini -scale %s -out thumbnail.jpg -zone %s" % (sys.executable, self.imageSize, app.currentZone), "r")
            app.clearBox("false event")
            app.renderedRegion==None
            app.renderedFullSize="Yes"
        else:
            # CCH -- made python exec name a variable.
            self.mapperScriptOutput=os.popen("%s mapper.py -settings mappergui.ini -scale %s -out thumbnail.jpg -zone %s -region %s" % ((sys.executable,) + app.getRegion()), "r")
            app.clearBox("false event")
            app.renderedRegion="Yes"
            app.renderedFullSize=None
            root.title(app.appName)
        os.chdir("..")
        self.currentIndex=0
        self.progressString=""
        self.stage=""
        self.process=""
        self.update()

    def update(self):
        text="%s" % self.mapperScriptOutput.readline()
        if text=="":
            self.renderMaster.after(100, self.renderMaster.destroy())
            app.griddingSize=app.getGridSize(app.imageSizeEntry.get())
            app.displayImage(self.imageSize)
        else:
            if str.find(text, "...")!=-1 and str.find(text, "Converting")!=-1:
                self.process=str.strip(text)
                self.currentIndex+=1
                self.logger.insert(self.currentIndex, self.process)
                self.logger.see(self.currentIndex)
            elif str.find(text, "...")!=-1:
                self.stage=str.strip(text)
                self.currentIndex+=1
                if self.currentIndex>2:
                    app.displayImage(self.imageSize)
            else:
                self.progressString="%s %s" % (self.stage, str.strip(text))
                self.logger.delete(self.currentIndex)
                self.logger.insert(self.currentIndex, self.progressString)
                self.logger.see(self.currentIndex)

            self.renderMaster.after_idle(self.update)

    def destroy(self):
        self.renderMaster.destroy()

class mainApplication:
    """Main application window. Everything starts here.

    Builds Main window, adds menus, controls for setting parameters, etc.
    """
    def __init__(self, master):
        self.appName="DAoC MapperGUI v2.5"
        self.appText="A simple graphical user interface to Oliver Jowett's brilliant DAoC Mapper.\n\nSee 'readme.txt' for installation.\n\nWritten by G. Willoughby\nsab@freeuk.com\n\nUpgraded to SI and TOA compatibility by Cynthia Higginbotham\ndragoness77@republicofnewhome.org"
        
        self.master=master
        master.withdraw()
        master.resizable(1, 1)
        master.title(self.appName)

        # Menu
        self.initMenu(master)

        # Map box
        self.initThumbnail(master)
        
        # Frame for controls below map box
        self.frame4 = Frame(master, bd=2, relief=GROOVE)
        self.frame4.grid(row=2, column=0)

        # Game Path
        Label(self.frame4, text="DAoC Game Path:", anchor=W).grid(row=0, column=0, padx=3, pady=3)
        self.gameEntry=Entry(self.frame4, relief=SUNKEN, width=43, insertofftime=150, insertontime=150)
        self.gameEntry.grid(row=0, column=1, padx=3, pady=3)
        Button(self.frame4, text="Browse...", width=10, command=self.setGameDir).grid(row=0, column=2, padx=3, pady=3)

        # Image size
        Label(self.frame4, text="Image size:", anchor=W).grid(row=0, column=3, padx=3, pady=3)
        self.imageSizeEntry=Entry(self.frame4, relief=SUNKEN, width=10, insertofftime=150, insertontime=150)
        self.imageSizeEntry.grid(row=0, column=4, padx=3, pady=3)
        self.imageSizeEntry.insert(0, "564")

        # Render Options
        self.initRenderOptions(master)
        
        # Frame for controls below Render Options box
        self.frame3 = Label(master, bd=2, relief=GROOVE)
        self.frame3.grid(row=2, column=1, ipadx=2, ipady=4)

        # Render Button
        self.renderButton=Button(self.frame3, text="Render", width=12,
                     command=self.render)
        self.renderButton.grid(row=0, column=0, padx=2)

        # Save Button
        self.saveButton=Button(self.frame3, text="Save Image...", width=12,
                       command=self.saveImage)
        self.saveButton.grid(row=0, column=1, padx=2)

        # Geometry
        master.update_idletasks()
        # CCH - use winfo_reqwidth instead.
        master.geometry("%dx%d+%d+%d" % (master.winfo_reqwidth(),
                         master.winfo_reqheight(),0, 0))
        master.deiconify()
        master.resizable(1, 1)
        master.focus_set()
        master.protocol('WM_DELETE_WINDOW', self.closeNicely)

        # Misc stuff
        self.currentZone=""
        self.readPrefs()
        self.rubberbandBox=None
        self.renderedRegion=None
        self.renderedFullSize=None
        self.batchRender=None
        self.griddingSize=self.getGridSize(self.imageSizeEntry.get())
        self.master.lift()
        if self.zone.locations==None:
            AboutBox(title="Game not found",
                 text="Please enter your gamepath below then exit and restart to populate the 'Zone' menu.")

    # Global functions
    def getGridSize(self, imageSize):
        return float(imageSize)/65.536

    def getRegion(self):
        imageSize=float(self.imageSizeEntry.get())
        coords=list(map(float, self.thumbnail.coords(self.rubberbandBox)))
        region=    (int(65535/imageSize*coords[0]),
                int(65535/imageSize*coords[1]),
                int(65535/imageSize*coords[2]),
                int(65535/imageSize*coords[3]))
        boxWidth=float(region[2])-float(region[0])
        boxHeight=float(region[3])-float(region[1])
        if boxWidth>boxHeight:
            scale=(65535.0/boxWidth)*100.0
        else:
            scale=(65535.0/boxHeight)*100.0
        newImageSize=int((imageSize/100.0)*scale)
        return newImageSize, self.currentZone, "%s %s %s %s" % (region)

    def mouseDown(self, event):
        self.startx = self.thumbnail.canvasx(event.x, self.griddingSize)
        self.starty = self.thumbnail.canvasy(event.y, self.griddingSize)

    def clearBox(self, event):
        self.thumbnail.delete(self.rubberbandBox)
        self.rubberbandBox=None

    def mouseMotion(self, event):
        imageSize=float(self.imageSizeEntry.get())
        self.finishx = self.thumbnail.canvasx(event.x, self.griddingSize)
        self.finishy = self.thumbnail.canvasy(event.y, self.griddingSize)
        if self.renderedRegion==None and self.currentZone!="":
            if (self.startx != self.thumbnail.canvasx(event.x)) and (self.starty != self.thumbnail.canvasy(event.y)):
                self.thumbnail.delete(self.rubberbandBox)
                self.rubberbandBox=self.thumbnail.create_rectangle(self.startx, self.starty, self.finishx, self.finishy, width=3)
                coords=list(map(float, self.thumbnail.coords(self.rubberbandBox)))
                if coords[0]<0 or coords[1]<0 or coords[2]>imageSize or coords[3]>imageSize:
                    self.thumbnail.delete(self.rubberbandBox)
                    self.rubberbandBox=self.thumbnail.create_rectangle(self.oldCoords, width=3)
                else:
                    self.oldCoords=[self.startx, self.starty, self.finishx, self.finishy]
                    self.master.update_idletasks()

    def activateCaptions(self, event):
        if self.rubberbandBox==None and self.currentZone!="" and self.renderedRegion!="Yes" and self.activeCaptionToggleVar.get()!=0 and self.renderedFullSize!=None:
            xCoord=(65535.0/float(self.imageSizeEntry.get())) * self.thumbnail.canvasx(event.x)
            yCoord=(65535.0/float(self.imageSizeEntry.get())) * self.thumbnail.canvasy(event.y)
            self.captionEditor=EditorMain(master="editorRoot",
                              zone="%s" % int(self.currentZone),
                              xCoord="%s" % int(xCoord),
                              yCoord="%s" % int(yCoord), oneClick="1")

    def selectRiverColour(self, event):
        try:
            import tkinter.colorchooser
            self.oldRiverColour = \
                  self.riverColourButton.itemcget(self.riverColourBox, "fill")
            self.riverColour= tkinter.colorchooser.askcolor(initialcolor=self.oldRiverColour, title=self.appName+" Colour Chooser")
            self.riverColourRGB="%s,%s,%s" % self.riverColour[0]
            self.riverColourHEX=self.riverColour[1]
            self.riverColourButton.itemconfig(self.riverColourBox, fill=self.riverColourHEX)
        except TypeError:
            pass

    def riverAlphaControl(self, event):
        self.riverAlphaAmount.set(self.riverAlphaScale.get())

    def bumpmapMinControl(self, event):
        sliderValue=float(self.bumpmapMinScale.get())/10
        self.bumpmapMinAmount.set(sliderValue)

    def bumpmapMaxControl(self, event):
        sliderValue=float(self.bumpmapMaxScale.get())/10
        self.bumpmapMaxAmount.set(sliderValue)

    def intervalControl(self, event):
        self.intervalAmount.set(self.intervalScale.get())

    def selectTreeColour(self, event):
        try:
            import tkinter.colorchooser
            self.oldTreeColour=self.treeColourButton.itemcget(self.treeColourBox, "fill")
            self.treeColour=tkinter.colorchooser.askcolor(initialcolor=self.oldTreeColour, title=self.appName+" Colour Chooser")
            self.treeColourRGB="%s,%s,%s" % self.treeColour[0]
            self.treeColourHEX=self.treeColour[1]
            self.treeColourButton.itemconfig(self.treeColourBox,
                             fill=self.treeColourHEX)
        except TypeError:
            pass

    def treeAlphaControl(self, event):
        self.treeAlphaAmount.set(self.treeAlphaScale.get())

    def treeMinControl(self, event):
        sliderValue=float(self.treeMinScale.get())/10
        self.treeMinAmount.set(sliderValue)

    def treeMaxControl(self, event):
        sliderValue=float(self.treeMaxScale.get())/10
        self.treeMaxAmount.set(sliderValue)

    def selectStructureColour(self, event):
        try:
            import tkinter.colorchooser
            self.oldStructureColour=self.structureColourButton.itemcget(self.structureColourBox, "fill")
            self.structureColour=tkinter.colorchooser.askcolor(initialcolor=self.oldStructureColour,
                title=self.appName+" Colour Chooser")
            self.structureColourRGB="%s,%s,%s" % self.structureColour[0]
            self.structureColourHEX=self.structureColour[1]
            self.structureColourButton.itemconfig(self.structureColourBox, fill=self.structureColourHEX)
        except TypeError:
            pass

    def structureAlphaControl(self, event):
        self.structureAlphaAmount.set(self.structureAlphaScale.get())

    def structureMinControl(self, event):
        sliderValue=float(self.structureMinScale.get())/10
        self.structureMinAmount.set(sliderValue)

    def structureMaxControl(self, event):
        sliderValue=float(self.structureMaxScale.get())/10
        self.structureMaxAmount.set(sliderValue)

    def selectBoundsColour(self, event):
        try:
            import tkinter.colorchooser
            self.oldBoundsColour=self.boundsColourButton.itemcget(self.boundsColourBox, "fill")
            self.boundsColour=tkinter.colorchooser.askcolor(initialcolor=self.oldBoundsColour,
                title=self.appName+" Colour Chooser")
            self.boundsColourRGB="%s,%s,%s" % self.boundsColour[0]
            self.boundsColourHEX=self.boundsColour[1]
            self.boundsColourButton.itemconfig(self.boundsColourBox, fill=self.boundsColourHEX)
        except TypeError:
            pass

    def boundsAlphaControl(self, event):
        self.boundsAlphaAmount.set(self.boundsAlphaScale.get())

    def outerGridAlphaControl(self, event):
        self.outerGridAlphaAmount.set(self.outerGridAlphaScale.get())

    def innerGridAlphaControl(self, event):
        self.innerGridAlphaAmount.set(self.innerGridAlphaScale.get())

    def selectCaptionsColour(self, event):
        try:
            import tkinter.colorchooser
            self.oldCaptionsColour=self.captionsColourButton.itemcget(self.captionsColourBox, "fill")
            self.captionsColour=tkinter.colorchooser.askcolor(initialcolor=self.oldCaptionsColour,
                title=self.appName+" Colour Chooser")
            self.captionsColourRGB="%s,%s,%s" % self.captionsColour[0]
            self.captionsColourHEX=self.captionsColour[1]
            self.captionsColourButton.itemconfig(self.captionsColourBox, fill=self.captionsColourHEX)
        except TypeError:
            pass

    def writeSettings(self):
        """Write MapperGUI's own settings file, 'settings.map'

        Saves all the parameters set in the GUI as future defaults.
        """
        settingsFile=open("settings.map", "w")
        settingsFile.write("%s\n" % self.backgroundOnOff.get())
        settingsFile.write("%s\n" % self.riverOnOff.get())
        settingsFile.write("%s\n" % self.riverColourHEX)
        settingsFile.write("%s\n" % self.riverAlphaScale.get())
        settingsFile.write("%s\n" % self.bumpMapOnOff.get())
        settingsFile.write("%s\n" % self.bumpmapMinScale.get())
        settingsFile.write("%s\n" % self.bumpmapMaxScale.get())
        settingsFile.write("%s\n" % self.contoursOnOff.get())
        settingsFile.write("%s\n" % self.intervalScale.get())
        settingsFile.write("%s\n" % self.treesOnOff.get())
        settingsFile.write("%s\n" % self.treeColourHEX)
        settingsFile.write("%s\n" % self.treeAlphaScale.get())
        settingsFile.write("%s\n" % self.treeMinScale.get())
        settingsFile.write("%s\n" % self.treeMaxScale.get())
        settingsFile.write("%s\n" % self.structuresOnOff.get())
        settingsFile.write("%s\n" % self.structureColourHEX)
        settingsFile.write("%s\n" % self.structureAlphaScale.get())
        settingsFile.write("%s\n" % self.structureMinScale.get())
        settingsFile.write("%s\n" % self.structureMaxScale.get())
        settingsFile.write("%s\n" % self.boundsOnOff.get())
        settingsFile.write("%s\n" % self.boundsColourHEX)
        settingsFile.write("%s\n" % self.boundsAlphaScale.get())
        settingsFile.write("%s\n" % self.outerGridOnOff.get())
        settingsFile.write("%s\n" % self.outerGridAlphaScale.get())
        settingsFile.write("%s\n" % self.innerGridOnOff.get())
        settingsFile.write("%s\n" % self.innerGridAlphaScale.get())
        settingsFile.write("%s\n" % self.captionsOnOff.get())
        settingsFile.write("%s\n" % self.captionsColourHEX)
        settingsFile.write("%s\n" % self.imageSizeEntry.get())
        settingsFile.write("%s\n" % self.boundsFillOnOff.get())
        settingsFile.write("%s\n" % self.bylineOnOff.get())
        settingsFile.write("%s\n" % self.bylineString.get())
        settingsFile.close()
    
    def readPrefs(self):
        """Read MapperGUI settings from settings file 'settings.map'
        """
        if os.path.isfile("settings.map"):
            settingsFile=open("settings.map", "r")
            prefs=settingsFile.readlines()
            for x in range(len(prefs)):
                prefs[x]=str.strip(prefs[x])
            settingsFile.close()
            self.backgroundOnOff.set(int(prefs[0]))
            self.riverOnOff.set(int(prefs[1]))
            self.riverColourHEX=prefs[2]
            self.riverColourButton.itemconfig(self.riverColourBox,
                              fill=self.riverColourHEX)
            self.riverAlphaScale.set(float(prefs[3]))
            self.bumpMapOnOff.set(int(prefs[4]))
            self.bumpmapMinScale.set(float(prefs[5]))
            self.bumpmapMaxScale.set(float(prefs[6]))
            self.contoursOnOff.set(int(prefs[7]))
            self.intervalScale.set(float(prefs[8]))
            self.treesOnOff.set(int(prefs[9]))
            self.treeColourHEX=prefs[10]
            self.treeColourButton.itemconfig(self.treeColourBox,
                             fill=self.treeColourHEX)
            self.treeAlphaScale.set(int(prefs[11]))
            self.treeMinScale.set(int(prefs[12]))
            self.treeMaxScale.set(int(prefs[13]))
            self.structuresOnOff.set(int(prefs[14]))
            self.structureColourHEX=prefs[15]
            self.structureColourButton.itemconfig(self.structureColourBox,
                                  fill=self.structureColourHEX)
            self.structureAlphaScale.set(int(prefs[16]))
            self.structureMinScale.set(int(prefs[17]))
            self.structureMaxScale.set(int(prefs[18]))
            self.boundsOnOff.set(int(prefs[19]))
            self.boundsColourHEX=prefs[20]
            self.boundsColourButton.itemconfig(self.boundsColourBox,
                               fill=self.boundsColourHEX)
            self.boundsAlphaScale.set(int(prefs[21]))
            self.outerGridOnOff.set(int(prefs[22]))
            self.outerGridAlphaScale.set(int(prefs[23]))
            self.innerGridOnOff.set(int(prefs[24]))
            self.innerGridAlphaScale.set(int(prefs[25]))
            self.captionsOnOff.set(int(prefs[26]))
            self.captionsColourHEX=prefs[27]
            self.captionsColourButton.itemconfig(self.captionsColourBox,
                                 fill=self.captionsColourHEX)
            self.gameEntry.delete(0, END)
            self.gameEntry.insert(INSERT, self.readLocalIni())
            self.imageSizeEntry.delete(0, END)
            self.imageSizeEntry.insert(0, prefs[28])
            self.boundsFillOnOff.set(int(prefs[29]))
            self.bylineOnOff.set(int(prefs[30]))
            self.bylineString.set(prefs[31])
            
    def hexToRgb(self, hexNumber):
        """Convert hex number in string format to RGB tuple

        in: hexnumber returns: (R,G,B)
        """
        n=eval('0x'+str(hexNumber)[1:])
        return (n>>16)&0xff, (n>>8)&0xff, n&0xff

    def render(self):
        if int(self.imageSizeEntry.get())> 65535:
            AboutBox(title="Image size too big",
                 text="Image size should be below 65535 pixels wide.")
            return 0
        if int(self.imageSizeEntry.get()) <= 10:
            AboutBox(title="Image size too small",
                 text="Image size should be more than 10 pixels wide. Really!")
            return 0
        if os.path.isfile("mapper/mapper.py"):
            self.writeSettings()
            settingsFile=open("settings.map", "r")
            prefs=settingsFile.readlines()
            for x in range(len(prefs)):
                prefs[x]=str.strip(prefs[x])
            settingsFile.close()
            CreateLocalINI(self.gameEntry.get())
            # send the 'CreateMapperINI' class RGB values NOT HEX!
            prefs[2]="%s,%s,%s" % self.hexToRgb(self.riverColourHEX)
            prefs[10]="%s,%s,%s" % self.hexToRgb(self.treeColourHEX)
            prefs[15]="%s,%s,%s" % self.hexToRgb(self.structureColourHEX)
            prefs[20]="%s,%s,%s" % self.hexToRgb(self.boundsColourHEX)
            prefs[27]="%s,%s,%s" % self.hexToRgb(self.captionsColourHEX)
            CreateMapperINI(prefs)
            if self.currentZone!="" and self.renderedRegion==None:
                self.progressBox=RenderBox()
            elif self.renderedRegion=="Yes":
                AboutBox(title="Region already rendered",
                     text="Please re-render a full zone to select another region.")
            else:
                AboutBox(title="No zone selected",
                     text="Please make sure your gamepath is entered correctly and you have selected a zone from the 'Zone' menu.")
        else:
            AboutBox(title="Couldn't find 'mapper.py'",
                 text="Unknown problem finding mapper files, try re-starting or re-installing. See 'readme.txt' for installation.")

    def displayImage(self, imageSize):
        """Display the most recently rendered map.

        Opens 'mapper/thumbnail.jpg' and displays in scrollbox.
        """
        try:
            self.currentImage=Image.open("mapper/thumbnail.jpg")
            self.currentPhotoImage=ImageTk.PhotoImage(self.currentImage)
            self.mapImage=self.thumbnail.create_image(0, 0, image=self.currentPhotoImage, anchor=NW)
            self.thumbnail.config(scrollregion=(0, 0, imageSize, imageSize))
            self.thumbnail.update()
        except IOError:
            pass

    def saveImage(self):
        """Save the recently rendered map to filename of choice

        Converts and saves 'mapper/thumbnail.jpg' to savePath and
        mode specified by user via tkFileDialog.
        """
        try:
            if self.currentImage:
                savePath=tkinter.filedialog.asksaveasfile(title="Save",
                filetypes=[("Jpeg File", ".jpg"),
                       ("PNG File", ".png"),("GIF 87a", ".gif")],
                       defaultextension=".jpg", 
                       initialdir="/usr/network/familiar/camelot")
                if savePath:
                    im = Image.open("mapper/thumbnail.jpg")
                    if savePath.name.endswith(".jpg"):
                        im.save(savePath.name, "JPEG", quality=100)
                    elif savePath.name.endswith(".png"):
                        im.save(savePath.name, "PNG")
                    elif savePath.name.endswith(".gif"):
                        im.save(savePath.name, "GIF")
        except AttributeError:
            pass

    def readLocalIni(self):
        """Read local.ini and check for correct gamepath
        """
        if os.path.isfile("mapper/local.ini"):
            # CCH -- changed to more Unix-appropriate path
            gamePath="c:/"
            localIniFile=open("mapper/local.ini","r")
            localIniLines=localIniFile.readlines()
            localIniFile.close()
            import re
            for x in range(len(localIniLines)):
                try:
                    if re.match("^gamepath", localIniLines[x]):
                        gamePath=str.split(localIniLines[x], " = ")[1]
                        gamePath=gamePath[:-1]
                except IndexError:
                    AboutBox(title="Corrupt file 'local.ini'",
                         text="The 'gamepath' parameter is missing from 'local.ini', a default game path will be entered. Please check this is right. See 'readme.txt' for installation.")
            return gamePath
        else:
            AboutBox(title="Couldn't find 'local.ini'",
                 text="The file 'local.ini' should be located in the '/mapper' folder. See 'readme.txt' for installation.")
            self.master.quit()

    def setGameDir(self):
        """Pop-up dialog to ask user to set correct gamePath.
        """
        self.gameEntry.delete(0, END)
        # CCH -- more Unix-appropriate path
        self.daocExe=tkinter.filedialog.askopenfilename(title=app.appName,
                              filetypes=[("DAoC Executable (camelot.exe)", ".exe")],
                              initialdir="/mnt/windows/Mythic/Camelot",
                              parent=self.master)
        self.gameDir=os.path.dirname(self.daocExe)
        self.gameEntry.insert(INSERT, self.gameDir)

    def closeNicely(self):
        """Save settings and quit
        """
        self.writeSettings()
        CreateLocalINI(self.gameEntry.get())
        self.master.quit()

    # Zone menu commands
    def zoneSelected(self, realm, menuName):
        """Menu command - zone selected

        Set title to new zone, and set currentZone == zone number.
        """
        self.master.title("%s - [%s : %s]" % (self.appName, realm, menuName))
        self.currentZone=menuName[:3]
        self.clearBox("event")
        self.renderedRegion=None

    def showCaptionEditor(self):
        """Menu command Open Caption Editor

        pop up caption editor
        """
        self.captionEditor=EditorMain(master="editorRoot")

    def showHelpBox(self):
        """Menu command Help

        pops up help text dialog.
        """
        HelpDialog(helpMaster="helpBox", helpfile="help/MapperGUI_Help.txt")

    def showAboutBox(self):
        """Menu command About

        pop up 'About' dialog
        """
        AboutBox(title=self.appName, text=self.appText, image="images/grail.gif")

    def initMenu(self, master):
        """initialize menus
        """
        # File
        self.menubar = Menu(master)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Save...", command=self.saveImage)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.closeNicely)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        # Zone Menu
        self.zone=Zones(self.readLocalIni())
        if self.zone.locations!=None:
            self.zonemenu = Menu(self.menubar, tearoff=0)
            self.albionmenu=Menu(self.menubar, tearoff=0)
            self.midgardmenu=Menu(self.menubar, tearoff=0)
            self.hibernianmenu=Menu(self.menubar, tearoff=0)
            self.atlantismenu=Menu(self.menubar, tearoff=0)
            self.frontiersmenu=Menu(self.menubar, tearoff=0)
##             self.miscmenu=Menu(self.menubar, tearoff=0)
            
            for x in range(len(self.zone.locations)):
                menuName=self.zone.locations[x][0]+" : " +self.zone.locations[x][1]
                zoneNumber=int(self.zone.locations[x][0])
                regionNumber = int(self.zone.locations[x][2])
                if regionNumber in [1,2,51]:    
                    realm="Albion"
                    self.albionmenu.add_command(label=menuName, command=GenericCallback(self.zoneSelected, realm, menuName))
                elif regionNumber in [100,102,151]:
                    realm="Midgard"
                    self.hibernianmenu.add_command(label=menuName, command=GenericCallback(self.zoneSelected, realm, menuName))
                elif regionNumber in [181,200,202]:
                    realm="Hibernia"
                    self.midgardmenu.add_command(label=menuName, command=GenericCallback(self.zoneSelected, realm, menuName))
                elif regionNumber in [70,71,72,73]:
                     realm="Atlantis"
                     self.atlantismenu.add_command(label=menuName, command=GenericCallback(self.zoneSelected, realm, menuName))
                elif regionNumber in [234,235,236,237,238,239,240,241,242,163]:
                    realm="Frontiers"
                    self.frontiersmenu.add_command(label=menuName, command=GenericCallback(self.zoneSelected, realm, menuName))
##                 elif regionNumber in [250,251,252,253]:
##                     realm="Unknown"
##                     self.miscmenu.add_command(label=menuName, command=GenericCallback(self.zoneSelected, realm, menuName))
            self.zonemenu.add_cascade(label="Albion", menu=self.albionmenu)
            self.zonemenu.add_cascade(label="Midgard", menu=self.hibernianmenu)
            self.zonemenu.add_cascade(label="Hibernia", menu=self.midgardmenu)
            self.zonemenu.add_separator()
            self.zonemenu.add_cascade(label="Atlantis", menu=self.atlantismenu)
            self.zonemenu.add_cascade(label="Frontiers", menu=self.frontiersmenu)
##             self.zonemenu.add_cascade(label="Misc.", menu=self.miscmenu)
            self.menubar.add_cascade(label="Zone", menu=self.zonemenu)

        # Options
        self.optionsmenu = Menu(self.menubar, tearoff=0)
        self.activeCaptionToggleVar = IntVar()
        self.optionsmenu.add_checkbutton(label="'OneClick' Captions", variable=self.activeCaptionToggleVar)
        self.activeCaptionToggleVar.set(0)
        self.optionsmenu.add_command(label="Open Caption Editor...", command=self.showCaptionEditor)
        self.optionsmenu.add_separator()
        self.optionsmenu.add_command(label="Help...", command=self.showHelpBox)
        self.optionsmenu.add_command(label="About...", command=self.showAboutBox)
        self.menubar.add_cascade(label="Options", menu=self.optionsmenu)
        master.config(menu=self.menubar)
        
    def initThumbnail(self, master):
        """initialize map scrollboxs
        """
        # Thumbnail Preview
        self.frame1=Frame(master, bd=2, relief=GROOVE)
        self.frame1.grid(row=0, column=0, rowspan=2)
        self.thumbnail=Canvas(self.frame1, bd=1, relief=SUNKEN, width=564, height=564, scrollregion=(0, 0, 564, 564))
        self.thumbnail.scrollX=Scrollbar(self.frame1, orient=HORIZONTAL)
        self.thumbnail.scrollY=Scrollbar(self.frame1, orient=VERTICAL)
        self.thumbnail['xscrollcommand']=self.thumbnail.scrollX.set
        self.thumbnail['yscrollcommand']=self.thumbnail.scrollY.set
        self.thumbnail.scrollX['command']=self.thumbnail.xview
        self.thumbnail.scrollY['command']=self.thumbnail.yview
        self.thumbnail.scrollX.pack(side=BOTTOM, fill=X)
        self.thumbnail.scrollY.pack(side=RIGHT, fill=Y)
        self.thumbnail.pack(side=LEFT)

        self.thumbnail.bind("<Button-1>", self.mouseDown)
        self.thumbnail.bind("<Button1-Motion>", self.mouseMotion)
        self.thumbnail.bind("<Button-3>", self.clearBox)
        self.thumbnail.bind("<Button3-Motion>", self.clearBox)

        self.thumbnail.bind("<ButtonRelease-1>", self.activateCaptions)
        
    def initRenderOptions(self, master):
        """initialize Render Options controls
        """
        # Frame
        self.frame2 = LabelFrame(master, labelText="Render Options", bd=2, relief=GROOVE)
        self.frame2.grid(row=0, column=1, ipadx=6, ipady=3, pady=11)

        spacer1=Canvas(self.frame2, width=2, height=4)
        spacer1.grid(row=0, column=0)
        self.lineWidth=150

        # Background
        self.backgroundOnOff=IntVar()
        self.backgroudSwitch=Checkbutton(self.frame2, text="Enable Background", variable=self.backgroundOnOff)
        self.backgroudSwitch.grid(row=1, column=0, sticky=W, columnspan=3)
        self.backgroundOnOff.set(1)
        Canvas(self.frame2, bd=1, width=self.lineWidth, relief=GROOVE, height=0).grid(row=2, column=0, columnspan=3)

        # River
        self.riverOnOff=IntVar()
        self.riverSwitch=Checkbutton(self.frame2, text="Enable Rivers", variable=self.riverOnOff)
        self.riverSwitch.grid(row=3, column=0, sticky=W, columnspan=2)
        self.riverOnOff.set(1)

        self.riverColourButton=Canvas(self.frame2, bd=1, width=26, relief=SUNKEN, height=15)
        self.riverColourButton.grid(row=3, column=2)
        self.riverColourHEX="#38B7FF"
        self.riverColourBox=self.riverColourButton.create_rectangle(2, 2, 29, 18, fill=self.riverColourHEX)
        self.riverColourButton.bind("<Button-1>", self.selectRiverColour)

        Label(self.frame2, text="Alpha:").grid(row=4, column=0)
        self.riverAlphaScale=Scale(self.frame2, bd=1, from_=0, to=255, orient=HORIZONTAL, sliderlength=15, width=9, length=60, takefocus=0, showvalue=0, command=self.riverAlphaControl)
        self.riverAlphaScale.grid(row=4, column=1)
        self.riverAlphaAmount=StringVar()
        self.riverAlphaLabel=Label(self.frame2, textvariable=self.riverAlphaAmount, width=4, bd=1, relief=SUNKEN)
        self.riverAlphaLabel.grid(row=4, column=2)

        Canvas(self.frame2, bd=1, width=self.lineWidth, relief=GROOVE, height=0).grid(row=5, column=0, columnspan=3)

        # Bumpmap
        self.bumpMapOnOff=IntVar()
        self.bumpMapSwitch=Checkbutton(self.frame2, text="Shade using bumpmap", variable=self.bumpMapOnOff)
        self.bumpMapSwitch.grid(row=6, column=0, sticky=W, columnspan=3)
        self.bumpMapOnOff.set(1)

        Label(self.frame2, text="Light(Min):").grid(row=7, column=0)
        self.bumpmapMinScale=Scale(self.frame2, bd=1, from_=0, to=35, orient=HORIZONTAL, sliderlength=15, width=9, length=60, takefocus=0, showvalue=0, command=self.bumpmapMinControl)
        self.bumpmapMinScale.grid(row=7, column=1)
        self.bumpmapMinAmount=StringVar()
        self.bumpmapMinLabel=Label(self.frame2, textvariable=self.bumpmapMinAmount, width=4, bd=1, relief=SUNKEN)
        self.bumpmapMinLabel.grid(row=7, column=2)

        Label(self.frame2, text="Light(Max):").grid(row=8, column=0)
        self.bumpmapMaxScale=Scale(self.frame2, bd=1, from_=0, to=35, orient=HORIZONTAL, sliderlength=15, width=9, length=60, takefocus=0, showvalue=0, command=self.bumpmapMaxControl)
        self.bumpmapMaxScale.grid(row=8, column=1)
        self.bumpmapMaxAmount=StringVar()
        self.bumpmapMaxLabel=Label(self.frame2, textvariable=self.bumpmapMaxAmount, width=4, bd=1, relief=SUNKEN)
        self.bumpmapMaxLabel.grid(row=8, column=2)

        Canvas(self.frame2, bd=1, width=self.lineWidth, relief=GROOVE, height=0).grid(row=9, column=0, columnspan=3)

        # Contours
        self.contoursOnOff=IntVar()
        self.contoursSwitch=Checkbutton(self.frame2, text="Overlay contours", variable=self.contoursOnOff)
        self.contoursSwitch.grid(row=10, column=0, sticky=W, columnspan=3)
        self.contoursOnOff.set(1)

        Label(self.frame2, text="Interval:").grid(row=11, column=0)
        self.intervalScale=Scale(self.frame2, bd=1, from_=0, to=1000, orient=HORIZONTAL,
                     sliderlength=15, width=9, length=60, takefocus=0,
                     showvalue=0, command=self.intervalControl)
        self.intervalScale.grid(row=11, column=1)
        self.intervalAmount=StringVar()
        self.intervalLabel=Label(self.frame2, textvariable=self.intervalAmount,
                     width=4, bd=1, relief=SUNKEN)
        self.intervalLabel.grid(row=11, column=2)

        Canvas(self.frame2, bd=1, width=self.lineWidth,
               relief=GROOVE, height=0).grid(row=12, column=0, columnspan=3)

        # Trees
        self.treesOnOff=IntVar()
        self.treesSwitch=Checkbutton(self.frame2, text="Draw trees",
                         variable=self.treesOnOff)
        self.treesSwitch.grid(row=13, column=0, sticky=W, columnspan=2)
        self.treesOnOff.set(1)

        self.treeColourButton=Canvas(self.frame2, bd=1, width=26,
                         relief=SUNKEN, height=15)
        self.treeColourButton.grid(row=13, column=2)
        self.treeColourHEX="#4DA43A"
        self.treeColourBox=self.treeColourButton.create_rectangle(2, 2, 29,
                                    18, fill=self.treeColourHEX)
        self.treeColourButton.bind("<Button-1>", self.selectTreeColour)

        Label(self.frame2, text="Alpha:").grid(row=14, column=0)
        self.treeAlphaScale=Scale(self.frame2, bd=1, from_=0, to=255,
                      orient=HORIZONTAL, sliderlength=15,
                      width=9, length=60, takefocus=0, showvalue=0,
                      command=self.treeAlphaControl)
        self.treeAlphaScale.grid(row=14, column=1)
        self.treeAlphaAmount=StringVar()
        self.treeAlphaLabel=Label(self.frame2, textvariable=self.treeAlphaAmount,
                      width=4, bd=1, relief=SUNKEN)
        self.treeAlphaLabel.grid(row=14, column=2)

        Label(self.frame2, text="Light(Min):").grid(row=15, column=0)
        self.treeMinScale=Scale(self.frame2, bd=1, from_=0, to=35,
                    orient=HORIZONTAL, sliderlength=15,
                    width=9, length=60, takefocus=0, showvalue=0,
                    command=self.treeMinControl)
        self.treeMinScale.grid(row=15, column=1)
        self.treeMinAmount=StringVar()
        self.treeMinLabel=Label(self.frame2, textvariable=self.treeMinAmount,
                    width=4, bd=1, relief=SUNKEN)
        self.treeMinLabel.grid(row=15, column=2)

        Label(self.frame2, text="Light(Max):").grid(row=16, column=0)
        self.treeMaxScale=Scale(self.frame2, bd=1, from_=0, to=35,
                    orient=HORIZONTAL, sliderlength=15,
                    width=9, length=60, takefocus=0, showvalue=0,
                    command=self.treeMaxControl)
        self.treeMaxScale.grid(row=16, column=1)
        self.treeMaxAmount=StringVar()
        self.treeMaxLabel=Label(self.frame2, textvariable=self.treeMaxAmount,
                    width=4, bd=1, relief=SUNKEN)
        self.treeMaxLabel.grid(row=16, column=2)

        Canvas(self.frame2, bd=1, width=self.lineWidth,
               relief=GROOVE, height=0).grid(row=17, column=0, columnspan=3)

        # Structures
        self.structuresOnOff=IntVar()
        self.structures=Checkbutton(self.frame2, text="Draw structures",
                        variable=self.structuresOnOff)
        self.structures.grid(row=18, column=0, sticky=W, columnspan=2)
        self.structuresOnOff.set(1)

        self.structureColourButton=Canvas(self.frame2, bd=1, width=26,
                          relief=SUNKEN, height=15)
        self.structureColourButton.grid(row=18, column=2)
        self.structureColourHEX="#DCDCDC"
        self.structureColourBox=self.structureColourButton.create_rectangle(2, 2,
                                            29, 18,
                                    fill=self.structureColourHEX)
        self.structureColourButton.bind("<Button-1>", self.selectStructureColour)

        Label(self.frame2, text="Alpha:").grid(row=19, column=0)
        self.structureAlphaScale=Scale(self.frame2, bd=1, from_=0, to=255,
                           orient=HORIZONTAL, sliderlength=15,
                           width=9, length=60, takefocus=0,
                           showvalue=0, command=self.structureAlphaControl)
        self.structureAlphaScale.grid(row=19, column=1)
        self.structureAlphaAmount=StringVar()
        self.structureAlphaLabel=Label(self.frame2,
                           textvariable=self.structureAlphaAmount,
                           width=4, bd=1, relief=SUNKEN)
        self.structureAlphaLabel.grid(row=19, column=2)

        Label(self.frame2, text="Light(Min):").grid(row=20, column=0)
        self.structureMinScale=Scale(self.frame2, bd=1, from_=0, to=35,
                         orient=HORIZONTAL, sliderlength=15,
                         width=9, length=60, takefocus=0, showvalue=0,
                         command=self.structureMinControl)
        self.structureMinScale.grid(row=20, column=1)
        self.structureMinAmount=StringVar()
        self.structureMinLabel=Label(self.frame2,
                         textvariable=self.structureMinAmount,
                         width=4, bd=1, relief=SUNKEN)
        self.structureMinLabel.grid(row=20, column=2)

        Label(self.frame2, text="Light(Max):").grid(row=21, column=0)
        self.structureMaxScale=Scale(self.frame2, bd=1, from_=0, to=35,
                         orient=HORIZONTAL, sliderlength=15,
                         width=9, length=60, takefocus=0, showvalue=0,
                         command=self.structureMaxControl)
        self.structureMaxScale.grid(row=21, column=1)
        self.structureMaxAmount=StringVar()
        self.structureMaxLabel=Label(self.frame2, textvariable=self.structureMaxAmount,
                         width=4, bd=1, relief=SUNKEN)
        self.structureMaxLabel.grid(row=21, column=2)

        Canvas(self.frame2, bd=1, width=self.lineWidth,
               relief=GROOVE, height=0).grid(row=22, column=0, columnspan=3)

        # Boundaries
        self.boundsOnOff=IntVar()
        self.bounds=Checkbutton(self.frame2, text="Draw edge boundaries",
                    variable=self.boundsOnOff)
        self.bounds.grid(row=23, column=0, sticky=W, columnspan=2)
        self.boundsOnOff.set(1)

        self.boundsColourButton=Canvas(self.frame2, bd=1, width=26,
                           relief=SUNKEN, height=15)
        self.boundsColourButton.grid(row=23, column=2)
        self.boundsColourHEX="#FFFFFF"
        self.boundsColourBox=self.boundsColourButton.create_rectangle(2, 2,
                                          29, 18,
                                   fill=self.boundsColourHEX)
        self.boundsColourButton.bind("<Button-1>", self.selectBoundsColour)

        Label(self.frame2, text="Alpha:").grid(row=24, column=0)
        self.boundsAlphaScale=Scale(self.frame2, bd=1, from_=0, to=255,
                        orient=HORIZONTAL, sliderlength=15,
                        width=9, length=60, takefocus=0, showvalue=0,
                        command=self.boundsAlphaControl)
        self.boundsAlphaScale.grid(row=24, column=1)
        self.boundsAlphaAmount=StringVar()
        self.boundsAlphaLabel=Label(self.frame2, textvariable=self.boundsAlphaAmount,
                        width=4, bd=1, relief=SUNKEN)
        self.boundsAlphaLabel.grid(row=24, column=2)

        # add fill/nofill option
        self.boundsFillOnOff=IntVar()
        self.boundsFill=Checkbutton(self.frame2, text="Shade behind boundaries",
                        variable=self.boundsFillOnOff)
        self.boundsFill.grid(row=25, column=0, columnspan=3)
        self.boundsFillOnOff.set(1)

        Canvas(self.frame2, bd=1, width=self.lineWidth,
               relief=GROOVE, height=0).grid(row=26, column=0, columnspan=3)

        # Main Grid
        self.outerGridOnOff=IntVar()
        self.outerGrid=Checkbutton(self.frame2, text="Draw main grid lines",
                       variable=self.outerGridOnOff)
        self.outerGrid.grid(row=27, column=0, sticky=W, columnspan=2)
        self.outerGridOnOff.set(1)

        Label(self.frame2, text="Alpha:").grid(row=28, column=0)
        self.outerGridAlphaScale=Scale(self.frame2, bd=1, from_=0, to=255,
                           orient=HORIZONTAL, sliderlength=15,
                           width=9, length=60, takefocus=0, showvalue=0,
                           command=self.outerGridAlphaControl)
        self.outerGridAlphaScale.grid(row=28, column=1)
        self.outerGridAlphaAmount=StringVar()
        self.outerGridAlphaLabel=Label(self.frame2,
                           textvariable=self.outerGridAlphaAmount,
                           width=4, bd=1, relief=SUNKEN)
        self.outerGridAlphaLabel.grid(row=28, column=2)

        Canvas(self.frame2, bd=1, width=self.lineWidth,
               relief=GROOVE, height=0).grid(row=29, column=0, columnspan=3)

        # Inner Grid
        self.innerGridOnOff=IntVar()
        self.innerGrid=Checkbutton(self.frame2,
                       text="Draw detailed grid lines",
                       variable=self.innerGridOnOff)
        self.innerGrid.grid(row=30, column=0, sticky=W, columnspan=2)
        self.innerGridOnOff.set(1)

        Label(self.frame2, text="Alpha:").grid(row=31, column=0)
        self.innerGridAlphaScale=Scale(self.frame2, bd=1, from_=0,
                           to=255, orient=HORIZONTAL, sliderlength=15,
                           width=9, length=60, takefocus=0, showvalue=0,
                           command=self.innerGridAlphaControl)
        self.innerGridAlphaScale.grid(row=31, column=1)
        self.innerGridAlphaAmount=StringVar()
        self.innerGridAlphaLabel=Label(self.frame2,
                           textvariable=self.innerGridAlphaAmount,
                           width=4, bd=1, relief=SUNKEN)
        self.innerGridAlphaLabel.grid(row=31, column=2)

        Canvas(self.frame2, bd=1, width=self.lineWidth,
               relief=GROOVE, height=0).grid(row=32, column=0, columnspan=3)

        # Captions
        self.captionsOnOff=IntVar()
        self.captions=Checkbutton(self.frame2, text="Draw captions",
                      variable=self.captionsOnOff)
        self.captions.grid(row=33, column=0, sticky=W, columnspan=2)
        self.captionsOnOff.set(0)

        self.captionsColourButton=Canvas(self.frame2, bd=1, width=26,
                         relief=SUNKEN, height=15)
        self.captionsColourButton.grid(row=33, column=2)
        self.captionsColourHEX="#000000"
        self.captionsColourBox=self.captionsColourButton.create_rectangle(2, 2,
                                          29, 18,
                                   fill=self.captionsColourHEX)
        self.captionsColourButton.bind("<Button-1>", self.selectCaptionsColour)
        
        Canvas(self.frame2, bd=1, width=self.lineWidth,
               relief=GROOVE, height=0).grid(row=34, column=0, columnspan=3)

        # Byline
        self.bylineOnOff=IntVar()
        self.bylineString=StringVar()
        self.bylineToggle=Checkbutton(self.frame2, text="Show Byline",
                           variable=self.bylineOnOff)
        self.bylineToggle.grid(row=35,column=0, sticky=W, columnspan=2)
        self.bylineOnOff.set(1)
        Label(self.frame2, text="Byline:").grid(row=36, column=0)
        self.bylineEntry = Entry(self.frame2, relief=SUNKEN, width=20,
                     insertofftime=150, insertontime=150,
                     textvariable=self.bylineString)
        self.bylineEntry.grid(row=36, column=1)

if __name__ == '__main__':
    root = Tk()
    app = mainApplication(root)
    root.mainloop()


# ChangeLog
# $Log: MapperGUI.pyw,v $
# Revision 1.15  2004/08/17 13:33:39  cyhiggin
# Changed version to 2.4 (live)
#
# Revision 1.14  2004/08/06 15:00:05  cyhiggin
# commented out rest of misc menu
#
# Revision 1.13  2004/08/06 14:55:48  cyhiggin
# commented out old BGs in menu
#
# Revision 1.12  2004/08/05 20:28:33  cyhiggin
# Started adding docstrings.
# Split up mainApplication.__init__ into __init__, initMenu,initThumbnail & initRenderOptions
# Added byline on/off toggle and byline entry field to GUI.
#
# Revision 1.11  2004/08/04 19:53:15  cyhiggin
# version is now 2.3.4b
#
# Revision 1.10  2004/07/28 21:21:28  cyhiggin
# Updated version to 2.3.3b.
#
# Revision 1.9  2004/06/17 18:51:25  cyhiggin
# Updated version tag
#
# Revision 1.8  2004/05/26 15:35:02  cyhiggin
# Added new battlegrounds to Frontiers region; increased resolution limits.
#
# Revision 1.7  2004/04/16 23:01:31  cyhiggin
# Added fill/no-fill option to boundary shading.
#
# Revision 1.6  2004/04/16 18:32:53  cyhiggin
# Added new save file types: PNG, GIF.
#
# Revision 1.5  2004/04/16 16:45:16  cyhiggin
# Determine which menu each zone goes under by region, not zone now.
# Added Frontiers menu, moved all New Frontiers zones there. Left old Battlefields under misc.
#
# Revision 1.4  2004/04/03 16:21:35  cyhiggin
# Changed version to 2.1
#
# Revision 1.3  2004/03/15 22:27:22  cyhiggin
# Modifications to MapperGUI and mapper modules to search for housing zones correctly.
#

