# -*- coding: UTF-8 -*-
import collections
import os

import tkinter as tk
from tkinter import ttk

import ttkwidgets as ttkw
from ttkwidgets import ScrolledListbox

import sqlite3
import math
from functools import partial
from types import SimpleNamespace

from PIL import Image
from PIL import ImageTk


root = tk.Tk()
root.geometry("%dx%d+0+0" % (root.winfo_screenwidth(), root.winfo_screenheight()) )
root.call("wm", "attributes", ".", "-fullscreen", "true") # Fullscreen mode
root.focus_set()

Pixel = tk.PhotoImage(width=1, height=1)
buttonShowPopup=tk.Button(text="Show Popup", command= lambda: playerAdd(root), image=Pixel, compound="center")
buttonClose=tk.Button(text="Close", command= lambda: root.destroy(), image=Pixel, compound="center")

buttonShowPopup.grid(row=0,column=0,sticky=tk.NSEW,padx=100,pady=100)
buttonClose.grid(row=1,column=0,sticky=tk.NSEW,padx=100,pady=100)

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)


def playerAdd(parent):
    def callback(event=None):
        popupRoot.destroy()
    # create popup window
    popupRoot = tk.Toplevel(bg="red")
    # create widgets
    popupPixel = tk.PhotoImage(width=1, height=1)
    popupWidgetEntry = tk.Entry(popupRoot)
    popupWidgetButtonClose = tk.Button(popupRoot, text="Close", command=lambda:popupRoot.destroy(), image=popupPixel, compound="center")
    # place on grid
    popupWidgetEntry.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)
    popupWidgetButtonClose.grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=10)
    #
    popupRoot.rowconfigure(0, weight=1)
    popupRoot.rowconfigure(1, weight=1)
    popupRoot.columnconfigure(0, weight=1)
    #
    popupWidgetEntry.focus()
    popupRoot.bind("<Return>", callback)
    # configure popup window
    popupRoot.title("Spieler hinzufügen")
    # popupRoot.overrideredirect(1)
    popupRoot.attributes("-topmost", True)  # Always keep window on top of others
    popupRoot.focus_set()
    popupRoot.grab_set() # make this the only accessible window
    popupRoot.geometry("%dx%d+%d+%d" % (400, 200, root.winfo_screenwidth() / 2 - 200, root.winfo_screenheight() / 2 - 100))
    # make parent window wait
    parent.wait_window(popupRoot)

root.mainloop()