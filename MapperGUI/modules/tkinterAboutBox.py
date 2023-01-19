# $Id: tkinterAboutBox.py,v 1.4 2004/08/05 18:26:25 cyhiggin Exp $
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

from tkinter import *

class AboutBox:
    """Displays About pop-up

    Creates a small modal dialog that displays information provided by caller.
    """
    def __init__(self, master="aboutRoot", title="Sample About Box...", text="Lorem ipsum dolor sit amet, consectetaur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", image=""):
        self.master=master
    # Setup window
        self.master=Toplevel()
    # Make it disappear
        self.master.withdraw()
        self.master.title("About")
        self.master.resizable(0, 0)

    # Enable the close button
        self.master.protocol('WM_DELETE_WINDOW', self.master.destroy)

    # Outer frame
        frame0=Frame(self.master)
        frame0.grid(row=0, column=0, padx=10, pady=10)

    # Icon
        if image!="":
            aboutIcon=Canvas(frame0, width=50, height=100)
            aboutIcon.grid(row=0, column=0, rowspan=3)
            icon=PhotoImage(file=image)
            aboutIcon.create_image(25, 50, image=icon)

    # Heading and text
        Label(frame0, text=title, justify=LEFT, anchor=W,
          font=("Arial", 12, "")).grid(row=1, column=1, sticky=W)
        Label(frame0, text=text, wraplength=200,
          justify=LEFT).grid(row=2, column=1)
        frame1=Frame(self.master, bd=0, relief=FLAT)
        frame1.grid(row=1, column=0)
        closeButton=Button(frame1, text="OK", width=10,
               underline=0, command=self.master.destroy)
        closeButton.grid(row=0, column=0, pady=5)
        closeButton.focus_set()
    # Align the window
        self.master.update_idletasks()
    # use winfo_reqwidth and winfo_reqheight instead of winfo_width & winfo_height,
    # as width & height are 0 when window is hidden in X windows.
        self.master.geometry("%dx%d+%d+%d"
                 % (self.master.winfo_reqwidth(),
                self.master.winfo_reqheight(),
                (self.master.winfo_screenwidth()/2)
                -(self.master.winfo_reqwidth()/2),
                (self.master.winfo_screenheight()/2)
                -(self.master.winfo_reqheight()/2)))
    # Make modal
        self.master.bind("<Return>", self.destroy)
        self.master.bind("<Alt-o>", self.destroy)
        self.master.deiconify()
        self.master.focus_set()
        self.master.grab_set()
        self.master.lift()
        self.master.wait_window()

    def destroy(self, event):
        self.master.destroy()

if __name__ == '__main__':
    root = Tk()
    app = AboutBox()
    root.mainloop()

# Change Log
# $Log: tkinterAboutBox.py,v $
# Revision 1.4  2004/08/05 18:26:25  cyhiggin
# Started adding docstrings
#
# Revision 1.3  2004/08/05 18:09:31  cyhiggin
# Added Id and Log tags
# Opens on top now (z-axis)
#


