import tkinter as tk
import ttkwidgets as ttkw
from ttkwidgets import ScrolledListbox
from PIL import Image
from PIL import ImageTk
from types import SimpleNamespace
import math

# ---------------------------------------------- #
# ------------- Create Namespaces -------------- #
# ---------------------------------------------- #

frames = SimpleNamespace()
widgets = SimpleNamespace()
SETTINGS = SimpleNamespace()

# ---------------------------------------------- #
# ------------- Create root window ------------- #
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

frames.teams = tk.Frame(frames.main, bg="orange")
frames.players = tk.Frame(frames.main, bg="pink")
frames.items = tk.Frame(frames.main, bg="green")
frames.total = tk.Frame(frames.main, bg="blue")

frames.teams.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
frames.players.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
frames.items.grid(row=0, column=2, sticky=tk.N+tk.S+tk.E+tk.W)
frames.total.grid(row=0, column=3, sticky=tk.N+tk.S+tk.E+tk.W)

frames.main.columnconfigure(0, weight=2)
frames.main.columnconfigure(1, weight=1)
frames.main.columnconfigure(2, weight=2)
frames.main.columnconfigure(3, weight=2)
frames.main.rowconfigure(0, weight=1)

frames.teams.grid_propagate(False)
frames.players.grid_propagate(False)
frames.items.grid_propagate(False)
frames.total.grid_propagate(False)

# ---------------------------------------------- #
# -------------Create Team Buttons ------------- #
# ---------------------------------------------- #

widgets.teambuttons = {}
widgets.teamimageson  = {}
widgets.teamimagesoff  = {}

SETTINGS.teamimagesize = int(root.winfo_screenwidth() / 7 * 2 / 3)

for i in range(16):
    # create buttons
    widgets.teambuttons[i] = tk.Radiobutton(frames.teams, text=str(i), value=i, indicatoron = tk.FALSE, bg="orange")
    widgets.teambuttons[i].grid(row=i // 3, column=i % 3, sticky=tk.NSEW, padx=0, pady=0)
    # load 'on' image
    img = Image.open("Logo_Südsee_On.gif")
    img = img.resize((SETTINGS.teamimagesize,SETTINGS.teamimagesize), resample=Image.LANCZOS)
    widgets.teamimageson[i] =  ImageTk.PhotoImage(img)
    widgets.teambuttons[i].config(image=widgets.teamimageson[i])
    # load 'off' image
    img = Image.open("Logo_Südsee_Off.gif")
    img = img.resize((SETTINGS.teamimagesize,SETTINGS.teamimagesize), resample=Image.LANCZOS)
    widgets.teamimagesoff[i] =  ImageTk.PhotoImage(img)
    widgets.teambuttons[i].config(selectimage=widgets.teamimagesoff[i])

# configure team frame so that contents scale
for col_num in range(frames.teams.grid_size()[0]):
    frames.teams.columnconfigure(col_num,weight=1)

for row_num in range(frames.teams.grid_size()[1]):
    frames.teams.rowconfigure(row_num,weight=1)

# ---------------------------------------------- #
# -------------Create Players Listbox ---------- #
# ---------------------------------------------- #

widgets.playerlistbox = ScrolledListbox(frames.players)
widgets.playerlistbox.grid(row=0, column=0, sticky=tk.NSEW)
widgets.playerlistbox.listbox.configure(font=("Courier", 30))

for i in range(30):
    widgets.playerlistbox.listbox.insert('end', 'player {}'.format(i))

frames.players.rowconfigure(0,weight=1)
frames.players.columnconfigure(0,weight=1)

# ---------------------------------------------- #
# -------------Create Item Frames -------------- #
# ---------------------------------------------- #

SETTINGS.items = SimpleNamespace()
SETTINGS.items.name = ["Wurst","Käse","Keks","Cola","Scheibe","Fanta","Schorle","Brisanti"]
SETTINGS.items.price = [2,1,3,4,12,1.5,1,1]
SETTINGS.items.categories = [0,1,2,0,2,0,3,0]

frames.itemcategories = {}

widgets.itembutton = {}

for i in range(len(set(SETTINGS.items.categories))):
    frames.itemcategories[i] = tk.Frame(frames.items, bg="red")
    frames.itemcategories[i].grid(column=0, row=i, sticky=tk.NSEW, padx=10, pady=10)

    print(SETTINGS.items.categories.count(sorted(set(SETTINGS.items.categories))[i]))
    rowweight = math.ceil(SETTINGS.items.categories.count(sorted(set(SETTINGS.items.categories))[i]) / 3)
    print(rowweight)

    frames.items.rowconfigure(i,weight=rowweight)
    frames.items.columnconfigure(0,weight=1)

for i in range(len(SETTINGS.items.name)):
    # create item button
    widgets.itembutton[i] = tk.Button(frames.itemcategories[SETTINGS.items.categories[i]], text=SETTINGS.items.name[i]+"\n"+str(SETTINGS.items.price[i])+"€", font=("Courier", 30))
    # figure out position of button widget in current category frame
    currentint = 0
    for j in range(i):
        if SETTINGS.items.categories[j] == SETTINGS.items.categories[i]:
            currentint = currentint +1
    # place widget in category frame
    widgets.itembutton[i].grid(row=(currentint)//3, column=(currentint)%3, sticky=tk.NSEW, pady=10, padx=10)

for i in range(len(frames.itemcategories)):
    for j in range(frames.itemcategories[i].grid_size()[0]):
        frames.itemcategories[i].columnconfigure(j,weight=1)
    for j in range(frames.itemcategories[i].grid_size()[1]):
        frames.itemcategories[i].rowconfigure(j,weight=1)

# ---------------------------------------------- #
# -------------Create Team Buttons ------------- #
# ---------------------------------------------- #

root.mainloop()