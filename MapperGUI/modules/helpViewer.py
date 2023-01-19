# $Id: helpViewer.py,v 1.2 2004/08/05 18:08:43 cyhiggin Exp $
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
import os

class HelpDialog:
	def __init__(self, helpMaster="helpBox", helpfile=""):
		self.helpMaster=helpMaster
		self.helpMaster=Toplevel()
		self.helpMaster.withdraw()
		# Enable the close button
		self.helpMaster.protocol('WM_DELETE_WINDOW', self.helpMaster.destroy)
		self.scrollbar = Scrollbar(self.helpMaster, orient=VERTICAL)
		self.helpText=Listbox(self.helpMaster, relief=SUNKEN, width=72, height=15, takefocus=0, yscrollcommand=self.scrollbar.set)
		self.scrollbar.config(command=self.helpText.yview)
		self.closeButton=Button(self.helpMaster, text="Close >>>", width=10, command=self.helpMaster.destroy)
		self.closeButton.pack(side=BOTTOM)
		self.scrollbar.pack(side=RIGHT, fill=Y)
		self.helpText.pack(side=LEFT, fill=BOTH, expand=1)
		openedHelpFile=open(helpfile, "r")
		helptext=openedHelpFile.readlines()
		for x in helptext:
			self.helpText.insert(END, x.strip())
		openedHelpFile.close()
		self.helpMaster.title("Help - [%s]" % os.path.split(helpfile)[1])
		self.helpText.bind("<Button-1>", self.noSelection)
		self.helpText.bind("<B1-Motion>", self.noSelection)
		self.helpText.bind("<ButtonRelease-1>", self.noSelection)
		self.helpMaster.update_idletasks()
		self.helpMaster.geometry("%dx%d+%d+%d" % (self.helpMaster.winfo_reqwidth(), self.helpMaster.winfo_reqheight(), (self.helpMaster.winfo_screenwidth()/2)-(self.helpMaster.winfo_reqwidth()/2)-95, (self.helpMaster.winfo_screenheight()/2)-(self.helpMaster.winfo_reqheight()/2)-40))
		self.helpMaster.deiconify()
		self.helpMaster.focus_set()
		self.closeButton.focus_set()
		self.helpMaster.grab_set()
		self.helpMaster.lift()
		self.helpMaster.wait_window()
	
	def noSelection(self, event):
		self.helpText.select_clear(0, END)

if __name__ == '__main__':
	os.chdir("../help")
	root=Tk()
	app=HelpDialog(helpMaster="helpBox", helpfile="MapperGUI_Help.txt")
	root.mainloop()

# Change Log
# $Log: helpViewer.py,v $
# Revision 1.2  2004/08/05 18:08:43  cyhiggin
# Enabled close button on frame.
# Added $Id$ and $Log$ tags.
# Opens on top.
#
