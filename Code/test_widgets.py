from tkinter import *
import tkinter.ttk as ttk
s=ttk.Style()
print('Style themes on my system are ', s.theme_names())
s.theme_use('clam')
s.configure('bb.TButton', background='white', padding=50)
b1=ttk.Button(text='Default')
b1.pack(side=LEFT, anchor=S, padx=[0,40])
b2=ttk.Button(text='Custom', style='bb.TButton')
b2.pack(side=RIGHT, anchor=S, padx=[20,0])