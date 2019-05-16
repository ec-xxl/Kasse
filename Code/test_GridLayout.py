import tkinter as tk
import ttkwidgets as ttkw
from ttkwidgets.frames import ScrolledFrame
from PIL import Image
from PIL import ImageTk
from types import SimpleNamespace

# ---------------------------------------------- #
# ------------- Create Main Frames ------------- #
# ---------------------------------------------- #

frames = SimpleNamespace()
widgets = SimpleNamespace()

# ---------------------------------------------- #
# ------------- Create Main Frames ------------- #
# ---------------------------------------------- #

root = tk.Tk()
root.overrideredirect(1) # Remove shadow & drag bar. Note: Must be used before wm calls otherwise these will be removed.
root.call("wm", "attributes", ".", "-topmost", "true") # Always keep window on top of others
root.geometry("%dx%d+0+0" % (root.winfo_screenwidth(), root.winfo_screenheight()) )
root.call("wm", "attributes", ".", "-fullscreen", "true") # Fullscreen mode
root.tk.call("::tk::unsupported::MacWindowStyle", "style", root._w, "plain", "none")
root.focus_set()

# ---------------------------------------------- #
# ------------- Create Main Frames ------------- #
# ---------------------------------------------- #

frames.main = tk.Frame(root, bg="red")
frames.statusbar = tk.Frame(root, bg="yellow")

frames.main.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
frames.statusbar.grid(row=1,column=0, sticky=tk.N+tk.S+tk.E+tk.W)

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0, minsize=50)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=0)

# ---------------------------------------------- #
# ------------- Create Subframees -------------- #
# ---------------------------------------------- #

frames.Teams = tk.Frame(frames.main, bg="orange")
frames.Players = tk.Frame(frames.main, bg="pink")
frames.Items = tk.Frame(frames.main, bg="green")
frames.Total = tk.Frame(frames.main, bg="blue")

frames.Teams.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
frames.Players.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
frames.Items.grid(row=0, column=2, sticky=tk.N+tk.S+tk.E+tk.W)
frames.Total.grid(row=0, column=3, sticky=tk.N+tk.S+tk.E+tk.W)

frames.main.columnconfigure(0, weight=2)
frames.main.columnconfigure(1, weight=1)
frames.main.columnconfigure(2, weight=2)
frames.main.columnconfigure(3, weight=2)
frames.main.rowconfigure(0, weight=1)

frames.Teams.grid_propagate(False)
frames.Players.grid_propagate(False)
frames.Items.grid_propagate(False)
frames.Total.grid_propagate(False)

# ---------------------------------------------- #
# -------------Create Team Buttons ------------- #
# ---------------------------------------------- #

p = {}
k = {}
b = {}

for i in range(16):
    b[i] = tk.Radiobutton(frames.Teams, text=str(i), value=i, indicatoron = tk.TRUE, bg="orange")
    b[i].grid(row=i // 3, column=i % 3, sticky=tk.NSEW, padx=5, pady=5)

for col_num in range(frames.Teams.grid_size()[0]):
    frames.Teams.columnconfigure(col_num,weight=1)

for row_num in range(frames.Teams.grid_size()[1]):
    frames.Teams.rowconfigure(row_num,weight=1)

for i in range(16):
    img = Image.open("Logo_Südsee_On.gif")
    # img = img.resize((b[i].winfo_width(), b[i].winfo_height()), Image.ANTIALIAS)
    img = img.resize((100,100), Image.ANTIALIAS)
    p[i] =  ImageTk.PhotoImage(img)
    b[i].config(image=p[i])
    img = Image.open("Logo_Südsee_Off.gif")
    # img = img.resize((b[i].winfo_width(), b[i].winfo_height()), Image.ANTIALIAS)
    # print(frames.Teams.winfo_width())
    img = img.resize((100,100), Image.ANTIALIAS)
    k[i] =  ImageTk.PhotoImage(img)
    b[i].config(selectimage=k[i])

# ---------------------------------------------- #
# -------------Create Team Buttons ------------- #
# ---------------------------------------------- #

root.mainloop()