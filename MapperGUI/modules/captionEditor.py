# MapperGUI: a GUI for 'Oliver Jowett's DAoC mapper.py'
# See http://www.randomly.org/projects/mapper/

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

from Tkinter import *
import tkMessageBox
from tkinterAboutBox import AboutBox
from helpViewer import HelpDialog
# import string, win32api, os
import string, os

class LabelFrame(Frame):
	def __init__(self, master, labelText="Sample text", **kwargs):
		Frame.__init__(self, master, kwargs)
		self.label=Label(master, text=" %s " % labelText)
		self.label.place(in_=self, relx=0, rely=0, x=6, y=-11)

class EditorMain:
	def __init__(self, master="editorRoot", zone="", xCoord="", yCoord="", oneClick="0"):
		self.master=master
		self.oneClick=oneClick
		# Set up window
		self.master=Toplevel()
		self.master.resizable(1, 1)
		self.master.withdraw()
		self.master.title("Caption Editor")
		#Menu
		self.menubar = Menu(self.master)
		self.filemenu = Menu(self.menubar, tearoff=0)
		self.filemenu.add_command(label="Exit", command=self.master.destroy)
		self.menubar.add_cascade(label="File", menu=self.filemenu, underline=0)

		self.helpmenu = Menu(self.menubar, tearoff=0)
		self.helpmenu.add_command(label="Help...", command=self.showHelpBox)
		self.menubar.add_cascade(label="Options", menu=self.helpmenu, underline=0)
#		self.zonemenu = Menu(self.menubar, tearoff=0)
#		self.albionToggleVar = IntVar()
#		self.zonemenu.add_checkbutton(label="Albion", variable=self.albionToggleVar, command=self.albionChecked)
#		self.albionToggleVar.set(0)
#		self.hiberniaToggleVar = IntVar()
#		self.zonemenu.add_checkbutton(label="Hibernia", variable=self.hiberniaToggleVar, command=self.hiberniaChecked)
#		self.hiberniaToggleVar.set(0)
#		self.midgardToggleVar = IntVar()
#		self.zonemenu.add_checkbutton(label="Midgard", variable=self.midgardToggleVar, command=self.midgardChecked)
#		self.midgardToggleVar.set(0)
#		self.zonemenu.add_separator()
#		self.allToggleVar = IntVar()
#		self.zonemenu.add_checkbutton(label="All", variable=self.allToggleVar, command=self.allChecked)
#		self.allToggleVar.set(1)
#		self.menubar.add_cascade(label="View", menu=self.zonemenu, underline=0)
		self.master.config(menu=self.menubar)
		# Label Frame
		self.labelFrame=Frame(self.master, bd=1, relief=RAISED)
		self.labelFrame.grid(row=0, column=0, padx=5, pady=0, sticky=W)
		# Labels
		Label(self.labelFrame, text="Zone", width=6).grid(row=0, column=0, sticky=W)
		Label(self.labelFrame, text="X Coord", width=7).grid(row=0, column=1, sticky=W)
		Label(self.labelFrame, text="Y Coord", width=7).grid(row=0, column=2, sticky=W)
		Label(self.labelFrame, text="Text", width=25).grid(row=0, column=3, sticky=W, columnspan=2)
		# List Frame
		self.dataFrame=Frame(self.master, bd=1, relief=SUNKEN)
		self.dataFrame.grid(row=1, column=0)
		# Listboxes
		self.scrollbar=Scrollbar(self.dataFrame, orient=VERTICAL)
		self.zoneList=Listbox(self.dataFrame, bd=0, takefocus=0, width=6, height=20, yscrollcommand=self.scrollbar.set, bg="#D4D0C8", exportselection=0)
		self.xCoordList=Listbox(self.dataFrame, bd=0, takefocus=0, width=8, height=20, yscrollcommand=self.scrollbar.set, bg="#C8C2B9", exportselection=0)
		self.yCoordList=Listbox(self.dataFrame, bd=0, takefocus=0, width=7, height=20, yscrollcommand=self.scrollbar.set, bg="#D4D0C8", exportselection=0)
		self.textList=Listbox(self.dataFrame, bd=0, takefocus=0, width=23, height=20, yscrollcommand=self.scrollbar.set, bg="#C8C2B9", exportselection=0)
		self.scrollbar.config(command=self.yview)
		self.zoneList.grid(row=0, column=0)
		self.xCoordList.grid(row=0, column=1)
		self.yCoordList.grid(row=0, column=2)
		self.textList.grid(row=0, column=3)
		self.scrollbar.grid(row=0, column=4, sticky=N+S)
		# Control Frame
		spacer1=Canvas(self.master, width=5, height=4)
		spacer1.grid(row=2, column=0)
		self.controlFrame=LabelFrame(self.master, labelText="Add new caption", bd=2, relief=GROOVE)
		self.controlFrame.grid(row=3, column=0, padx=5, pady=5, ipadx=5, ipady=8)
		# Controls
		Label(self.controlFrame, text="Zone ID:").grid(row=0, column=0, padx=4, pady=2, sticky=W)
		self.zoneListEntry=Entry(self.controlFrame, width=4, insertofftime=150, insertontime=150)
		self.zoneListEntry.grid(row=0, column=1, padx=0, pady=4, sticky=W)
		Label(self.controlFrame, text="X Coord:").grid(row=0, column=2, padx=4, pady=2, sticky=W)
		self.xCoordListEntry=Entry(self.controlFrame, width=6, insertofftime=150, insertontime=150)
		self.xCoordListEntry.grid(row=0, column=3, padx=0, pady=4, sticky=W)
		Label(self.controlFrame, text="Y Coord:").grid(row=0, column=4, padx=4, pady=2, sticky=W)
		self.yCoordListEntry=Entry(self.controlFrame, width=6, insertofftime=150, insertontime=150)
		self.yCoordListEntry.grid(row=0, column=5, padx=0, pady=4, sticky=W)
		Label(self.controlFrame, text="Caption:").grid(row=1, column=0, padx=4, pady=2, sticky=W)
		self.textListEntry=Entry(self.controlFrame, width=37, insertofftime=150, insertontime=150)
		self.textListEntry.grid(row=1, column=1, columnspan=5, sticky=W)
		spacer1=Canvas(self.controlFrame, width=5, height=3)
		spacer1.grid(row=2, column=0)
		# Button frame
		self.buttonFrame=Frame(self.controlFrame)
		self.buttonFrame.grid(row=3, column=0, columnspan=6)
		Button(self.buttonFrame, text="Close", width=10, command=self.master.destroy).grid(row=0, column=0, sticky=W)
		Button(self.buttonFrame, text="Delete", width=10, command=self.deleteEntry).grid(row=0, column=1, padx=26)
		self.addUpdateButton=Button(self.buttonFrame, text="Add >>>", width=10, command=self.addNew)
		self.addUpdateButton.grid(row=0, column=2, sticky=E)
		# Align the window
		self.master.update_idletasks()

		self.master.geometry("%dx%d+%d+%d" % (self.master.winfo_reqwidth(), self.master.winfo_reqheight(), (self.master.winfo_screenwidth()/2)-(self.master.winfo_reqwidth()/2), (self.master.winfo_screenheight()/2)-(self.master.winfo_reqheight()/2)))

		self.master.deiconify()
		self.master.resizable(1, 1)
		self.master.lift()
		self.master.focus_set()
		self.master.grab_set()

		self.zoneList.bind("<Button-1>", self.selectAllIndices)
		self.zoneList.bind("<B1-Motion>", self.selectAllIndices)
		self.xCoordList.bind("<Button-1>", self.selectAllIndices)
		self.xCoordList.bind("<B1-Motion>", self.selectAllIndices)
		self.yCoordList.bind("<Button-1>", self.selectAllIndices)
		self.yCoordList.bind("<B1-Motion>", self.selectAllIndices)
		self.textList.bind("<Button-1>", self.selectAllIndices)
		self.textList.bind("<B1-Motion>", self.selectAllIndices)

		self.zoneList.bind("<Double-Button-1>", self.editEntry)
		self.xCoordList.bind("<Double-Button-1>", self.editEntry)
		self.yCoordList.bind("<Double-Button-1>", self.editEntry)
		self.textList.bind("<Double-Button-1>", self.editEntry)
		
		self.master.bind("<Return>", self.eventaddNew)
		self.selected=None
		self.readCaptionsINI()

		self.zoneListEntry.insert(0, zone)
		self.xCoordListEntry.insert(0, xCoord)
		self.yCoordListEntry.insert(0, yCoord)

		if oneClick=="0":
			self.zoneListEntry.focus_set()
		else:
			self.textListEntry.focus_set()

	def yview(self, *args):
		apply(self.zoneList.yview, args)
		apply(self.xCoordList.yview, args)
		apply(self.yCoordList.yview, args)
		apply(self.textList.yview, args)

#	def albionChecked(self):
#		self.hiberniaToggleVar.set(0)
#		self.midgardToggleVar.set(0)
#		self.allToggleVar.set(0)
#	
#	def hiberniaChecked(self):
#		self.albionToggleVar.set(0)
#		self.midgardToggleVar.set(0)
#		self.allToggleVar.set(0)
#
#	def midgardChecked(self):
#		self.albionToggleVar.set(0)
#		self.hiberniaToggleVar.set(0)
#		self.allToggleVar.set(0)
#
#	def allChecked(self):
#		self.albionToggleVar.set(0)
#		self.hiberniaToggleVar.set(0)
#		self.midgardToggleVar.set(0)

	def editEntry(self, event):
		self.zoneListEntry.delete(0, END)
		self.xCoordListEntry.delete(0, END)
		self.yCoordListEntry.delete(0, END)
		self.textListEntry.delete(0, END)
		self.zoneListEntry.insert(0, self.zoneList.get(ACTIVE))
		self.xCoordListEntry.insert(0, self.xCoordList.get(ACTIVE))
		self.yCoordListEntry.insert(0, self.yCoordList.get(ACTIVE))
		self.textListEntry.insert(0, self.textList.get(ACTIVE))
		self.updatedEntryIndex=int(self.zoneList.curselection()[0])
		self.addUpdateButton.config(text="Update >>>", command=self.updateEditedEntry)
		self.master.bind("<Return>", self.updateEditedEntryEvent)

	def updateEditedEntryEvent(self, event):
		self.updateEditedEntry()
	
	def updateEditedEntry(self):
		try:
			zoneNumber=int(self.zoneListEntry.get())
		except ValueError:
			AboutBox(title="Invalid 'Zone ID'", text="The 'Zone ID' should be a number with no leading zero's (i.e. for Campacorentin Forest in Albion type '8'). See the main application's 'Zone' menu for current zone id's.")
			self.zoneListEntry.focus_set()
			return 0
		try:
			xCoord=int(self.xCoordListEntry.get())
			if xCoord>65535:
				raise ValueError
		except ValueError:
			AboutBox(title="Invalid 'X Coord'", text="The 'X Coord' should be a number below 65535 with no leading zero's.")
			self.xCoordListEntry.focus_set()
			return 0
		try:
			yCoord=int(self.yCoordListEntry.get())
			if yCoord>65535:
				raise ValueError
		except ValueError:
			AboutBox(title="Invalid 'Y Coord'", text="The 'Y Coord' should be a number below 65535 with no leading zero's.")
			self.yCoordListEntry.focus_set()
			return 0
		if self.textListEntry.get()=="":
			AboutBox(title="No 'Caption' entered", text="Please enter a caption in the 'Caption' field.")
			self.textListEntry.focus_set()
			return 0
		else:
			newText=string.strip(self.textListEntry.get())
		# Add new data to lists
		self.addUpdateButton.config(text="Add >>>", command=self.addNew)
		self.master.bind("<Return>", self.eventaddNew)
		self.zoneList.delete(self.updatedEntryIndex)
		self.xCoordList.delete(self.updatedEntryIndex)
		self.yCoordList.delete(self.updatedEntryIndex)
		self.textList.delete(self.updatedEntryIndex)
		self.zoneList.insert(self.updatedEntryIndex-1, zoneNumber)
		self.xCoordList.insert(self.updatedEntryIndex-1, xCoord)
		self.yCoordList.insert(self.updatedEntryIndex-1, yCoord)
		self.textList.insert(self.updatedEntryIndex-1, newText)
		self.writeCaptionsINI()
		self.clearAllFields()

	def eventaddNew(self, event):
		self.addNew()

	def addNew(self):
		try:
			zoneNumber=int(self.zoneListEntry.get())
		except ValueError:
			AboutBox(title="Invalid 'Zone ID'", text="The 'Zone ID' should be a number with no leading zero's (i.e. for Campacorentin Forest in Albion type '8'). See the main application's 'Zone' menu for current zone id's.")
			self.zoneListEntry.focus_set()
			return 0
		try:
			xCoord=int(self.xCoordListEntry.get())
			if xCoord>65535:
				raise ValueError
		except ValueError:
			AboutBox(title="Invalid 'X Coord'", text="The 'X Coord' should be a number below 65535 with no leading zero's.")
			self.xCoordListEntry.focus_set()
			return 0
		try:
			yCoord=int(self.yCoordListEntry.get())
			if yCoord>65535:
				raise ValueError
		except ValueError:
			AboutBox(title="Invalid 'Y Coord'", text="The 'Y Coord' should be a number below 65535 with no leading zero's.")
			self.yCoordListEntry.focus_set()
			return 0
		if self.textListEntry.get()=="":
			AboutBox(title="No 'Caption' entered", text="Please enter a caption in the 'Caption' field.")
			self.textListEntry.focus_set()
			return 0
		else:
			newText=string.strip(self.textListEntry.get())
		# Add new data to lists
		self.zoneList.insert(END , zoneNumber)
		self.xCoordList.insert(END , xCoord)
		self.yCoordList.insert(END , yCoord)
		self.textList.insert(END , newText)
		self.writeCaptionsINI()
		self.clearAllFields()

		if self.oneClick=="0":
			self.zoneListEntry.focus_set()
		else:
			self.master.destroy()


	def clearAllFields(self):
			self.zoneListEntry.delete(0, END)
			self.zoneList.select_clear(0, END)
			self.xCoordListEntry.delete(0, END)
			self.xCoordList.select_clear(0, END)
			self.yCoordListEntry.delete(0, END)
			self.yCoordList.select_clear(0, END)
			self.textListEntry.delete(0, END)
			self.textList.select_clear(0, END)
			self.zoneListEntry.focus_set()

	def selectAllIndices(self, event):
		self.selected="True"
		self.zoneList.select_clear(0, END)
		self.zoneList.activate(self.zoneList.nearest(event.y))
		self.zoneList.select_set(self.zoneList.nearest(event.y))
		self.xCoordList.select_clear(0, END)
		self.xCoordList.activate(self.xCoordList.nearest(event.y))
		self.xCoordList.select_set(self.xCoordList.nearest(event.y))
		self.yCoordList.select_clear(0, END)
		self.yCoordList.activate(self.yCoordList.nearest(event.y))
		self.yCoordList.select_set(self.yCoordList.nearest(event.y))
		self.textList.select_clear(0, END)
		self.textList.activate(self.textList.nearest(event.y))
		self.textList.select_set(self.textList.nearest(event.y))

	def deleteEntry(self):
		if self.selected=="True":
			## CCH - replaced win32-specific MessageBox with generic tkMessageBox
			if tkMessageBox.askyesno("Delete", "Are you sure you want to remove this entry?", parent=self.master):
				
## 			if win32api.MessageBox(0,"Are you sure you want to remove this entry?", "Delete", 1, 0) == 1:
				self.zoneList.delete(self.textList.index(ACTIVE))
				self.xCoordList.delete(self.textList.index(ACTIVE))
				self.yCoordList.delete(self.textList.index(ACTIVE))
				self.textList.delete(self.textList.index(ACTIVE))
				self.writeCaptionsINI()
		else:
			AboutBox(title="No caption selected", text="Please select a caption to delete.")

	def writeCaptionsINI(self):
		rawCaptions=[]
		for x in range(self.zoneList.size()):
			rawCaptions.append("%s,%s,%s = %s" % (self.zoneList.get(x),self.xCoordList.get(x),self.yCoordList.get(x),self.textList.get(x)))
		dataFile=open(	"mapper/captions.ini", "w")
		dataFile.write("[town-captions]\n")
		rawCaptions.sort()
		for x in range(len(rawCaptions)):
			dataFile.write("%s\n" % rawCaptions[x])
		dataFile.close()
		self.readCaptionsINI()

	def readCaptionsINI(self):
		self.selected=None
		self.zoneList.delete(0, END)
		self.xCoordList.delete(0, END)
		self.yCoordList.delete(0, END)
		self.textList.delete(0, END)
		dataFile=open(	"mapper/captions.ini", "r")
		rawCaptions=dataFile.readlines()
		rawCaptions.pop(0)
		for x in range(len(rawCaptions)):
			# Sort out data
			rawCaptions[x]=string.split(string.strip(rawCaptions[x]), ",")
			lastCoord=string.split(rawCaptions[x][2], "=")[0]
			location=string.split(rawCaptions[x][2], "=")[1]
			rawCaptions[x][2]=string.strip(lastCoord)
			rawCaptions[x].append(string.strip(location))
			# Populate grids
			self.zoneList.insert(END , rawCaptions[x][0])
			self.xCoordList.insert(END , rawCaptions[x][1])
			self.yCoordList.insert(END , rawCaptions[x][2])
			self.textList.insert(END , rawCaptions[x][3])
		dataFile.close()

	def showHelpBox(self):
		HelpDialog(helpMaster="helpBox", helpfile="help/CaptionEditor_Help.txt")

if __name__ == '__main__':

	root=Tk()
	os.chdir("..")
	app=EditorMain()
	root.mainloop()
