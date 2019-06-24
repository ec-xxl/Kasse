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

import platform

# ---------------------------------------------- #
# ------------- Create Namespaces -------------- #
# ---------------------------------------------- #

frames = SimpleNamespace()
widgets = SimpleNamespace()
assets = SimpleNamespace()
SETTINGS = SimpleNamespace()
selection = SimpleNamespace()

# ---------------------------------------------- #
# ------------- Create root window ------------- #
# ---------------------------------------------- #

root = tk.Tk()
print(platform.system())
if platform.system() == "Darwin":
    root.overrideredirect(1) # Remove shadow & drag bar. Note: Must be used before wm calls otherwise these will be removed.
    root.call("wm", "attributes", ".", "-topmost", "true") # Always keep window on top of others
    root.geometry("%dx%d+0+0" % (root.winfo_screenwidth(), root.winfo_screenheight()) )
    root.call("wm", "attributes", ".", "-fullscreen", "true") # Fullscreen mode
    root.tk.call("::tk::unsupported::MacWindowStyle", "style", root._w, "plain", "none")
    root.focus_set()
else:
    # root.call("wm", "attributes", ".", "-topmost", "true") # Always keep window on top of others
    root.geometry("%dx%d+0+0" % (root.winfo_screenwidth(), root.winfo_screenheight()) )
    root.call("wm", "attributes", ".", "-fullscreen", "true") # Fullscreen mode
    root.focus_set()

# ---------------------------------------------- #
# ------------- global variables --------------- #
# ---------------------------------------------- #

selectedTeam = tk.StringVar()
selectedItems = collections.OrderedDict()
displayedPlayers = []

# -------------------------------------------------------------------------------------------- #
# ----------------------------------- Functions ---------------------------------------------- #
# -------------------------------------------------------------------------------------------- #

# ---------------------------------------------- #
# ------------- General ------------------------ #
# ---------------------------------------------- #

# show error message
def popupError(s):
    popupRoot = tk.Tk()
    popupRoot.overrideredirect(1) # Remove shadow & drag bar. Note: Must be used before wm calls otherwise these will be removed.
    popupRoot.call("wm", "attributes", ".", "-topmost", "true") # Always keep window on top of others
    popupRoot.after(2000, lambda: popupRoot.destroy())          # Time in Miliseconds 2000 = 2 seconds
    popupButton = tk.Label(popupRoot, text=s, font=("Verdana", 20), bg="yellow")
    popupButton.pack(expand=1, fill="both")
    popupRoot.geometry("%dx%d+%d+%d" % (400, 100, root.winfo_screenwidth()/2 - 200, root.winfo_screenheight()/2 - 50 ))
    popupRoot.focus_set()
    popupRoot.mainloop()

# SQLite related
def runQuery(sql, data=None, receive=False):
    conn = sqlite3.connect("kasse.db")
    cursor = conn.cursor()
    if data:
        cursor.execute(sql, data)
    else:
        cursor.execute(sql)

    if receive:
        return cursor.fetchall()
    else:
        conn.commit()
    conn.close()

# ---------------------------------------------- #
# ------------- Selection Actions -------------- #
# ---------------------------------------------- #

def onSelectTeam(team: str):
    displayPlayers(team)

def onClickItem(name: str, price:float):
    if (name, price) not in selectedItems:
        selectedItems[(name, price)] = 0
    selectedItems[(name, price)] += 1
    displayOrder()

def onSelectOrder(evt):
    global selectedItems
    curItem = widgets.totalTreeViewItems.focus()
    item = widgets.totalTreeViewItems.item(curItem)
    key = (item.get('tags')[0], float(item.get('tags')[1]))
    quantity = selectedItems[key] - 1
    selectedItems[key] = quantity
    if quantity == 0:
        del selectedItems[key]
    displayOrder()

def displayPlayers(team: str):
    players = widgets.playerTreeView.get_children()
    if players != '()':
        for player in players:
            widgets.playerTreeView.delete(player)  # delete current entries
    players = get_players(team)                     # get players of Team
    global displayedPlayers
    displayedPlayers = players
    for player_id, player, is_payed in players:
        widgets.playerTreeView.insert("", "end", text=player, values=("x" if is_payed else ""), tags=player_id)
    updateTotal()


# ---------------------------------------------- #
# ------------- Info get ----------------------- #
# ---------------------------------------------- #

def get_players(team: str):
    select_player = "SELECT id, player_name, is_payed FROM players WHERE team_name = ?"
    players = runQuery(select_player, (team,), receive=tk.TRUE)
    return players

def getSelectedTeam():
    return selectedTeam.get()

def getSelectedPlayerID():

    if widgets.playerTreeView.focus():
        curPlayer = widgets.playerTreeView.focus()
        player = widgets.playerTreeView.item(curPlayer)
        return int(player.get('tags')[0])
    else:
        popupError("Bitte einen Spieler auswählen")

# ---------------------------------------------- #
# ------------- Button Actions ----------------- #
# ---------------------------------------------- #

def addPlayer():
    def callback(event=None):
        if e.get():
            team = getSelectedTeam()
            player = e.get()  # This is the text you may want to use later
            insert_player = "INSERT INTO players (player_name, team_name) VALUES (?, ?)"    # SQL-String
            runQuery(insert_player, (player, team))     # add to Database
            displayPlayers(team)    # add to Listbox
            popup.destroy()

    if getSelectedTeam():
        popup = tk.Tk()
        popup.attributes("-topmost", True)
        popup.focus_set()
        e = tk.Entry(popup)
        e.pack()
        e.focus()
        popButton = tk.Button(popup, text="OK", width=10, command=lambda: callback())
        popButton.pack()
        popup.bind("<Return>", callback)
        popup.mainloop()
    else:
        popupError("Bitte ein Team auswählen")

def renamePlayer():
    def callback(event=None):
        if e.get():
            team = getSelectedTeam()
            playerID = getSelectedPlayerID()
            player_name = e.get()  # Entry of new name
            update_player = "UPDATE players SET player_name = ? WHERE id = ?"    # SQL-String
            runQuery(update_player, (player_name, playerID))     # add to Database
            displayPlayers(team)    # add to Listbox
            popup.destroy()

    if getSelectedPlayerID():

        popup = tk.Tk()
        popup.attributes("-topmost", True)
        e = tk.Entry(popup)
        e.pack()
        e.focus()
        popButton = tk.Button(popup, text="OK", width=10, command=lambda: callback())
        popButton.pack()
        popup.bind("<Return>", callback)
        popup.mainloop()
    else:
        popupError("Bitte einen Spieler auswählen")

def confirmOrder():
    global selectedItems
    player_id = getSelectedPlayerID()
    if player_id:
        for item in selectedItems:
            insert_order = "INSERT INTO purchases (player_id, item_name, price, item_quantity, payed) VALUES (?, ?, ?, ?, ?)"
            data = (player_id, item[0], item[1], selectedItems[item], 0)
            runQuery(insert_order, data)
        selectedItems = {}
        selectedTeam.set("")        # Unselect Team
        displayPlayers("")          # Show empty Player List
        displayOrder()

def stornoOrder():
    global selectedItems
    player_id = getSelectedPlayerID()
    if player_id:
        for item in selectedItems:
            insert_order = "INSERT INTO purchases (player_id, item_name, price, item_quantity, payed) VALUES (?, ?, ?, ?, ?)"
            data = (player_id, item[0], -item[1], selectedItems[item], 0)
            runQuery(insert_order, data)
        selectedItems = {}
        selectedTeam.set("")        # Unselect Team
        displayPlayers("")          # Show empty Player List
        displayOrder()

def deleteOrder():
    global selectedItems
    selectedItems = collections.OrderedDict()
    displayOrder()

def popupPay():
    playerID = getSelectedPlayerID()
    if playerID:
        # create window
        popPay = tk.Tk()
        popPay.overrideredirect(1) # Remove shadow & drag bar. Note: Must be used before wm calls otherwise these will be removed.
        popPay.attributes("-topmost", True)
        popPay.geometry("%dx%d+%d+%d" % (400, 300, root.winfo_screenwidth() / 2 - 200, root.winfo_screenheight() / 2 - 150))
        popPay.call("wm", "attributes", ".", "-topmost", "true") # Always keep window on top of others
        # create Listbox
        popListbox = tk.Listbox(popPay)

        # sum up purchases
        select_purchases = "SELECT item_name, price, SUM(item_quantity) FROM purchases WHERE player_id = ? AND payed = 0 GROUP BY item_name, price"
        purchases = runQuery(select_purchases, (playerID,), receive=tk.TRUE)
        total = 0
        for purchase in purchases:
            popListbox.insert(tk.END, purchase[0]+" "+str(purchase[1])+"€ x "+str(purchase[2]))
            total += purchase[1]*purchase[2]

        def deduction():
            pay_purchases = "UPDATE purchases SET payed = 1 WHERE player_id = ?"
            runQuery(pay_purchases, (playerID,))
            popPay.destroy()

        # create labels and buttons
        popLabelTotal = tk.Label(popPay, text="Summe der Einkäufe %.2f€" % total)
        popLabelPaid = tk.Label(popPay, text="Bisher bezahlt %.2f€" % -1)
        popLabelDue = tk.Label(popPay, text="Übrig %.2f€" % -1)
        popButtonPay = tk.Button(popPay, text="Bezahlen", width=10, command=deduction)
        popButtonAbort = tk.Button(popPay, text="Abbrechen", width=10, command=lambda: popPay.destroy())

        # place widgets on grid
        popListbox.grid(column=0, row=0, sticky=tk.NSEW)
        popLabelTotal.grid(column=0, row=1, sticky=tk.NSEW)
        popLabelPaid.grid(column=0, row=2, sticky=tk.NSEW)
        popLabelDue.grid(column=0, row=3, sticky=tk.NSEW)
        popButtonPay.grid(column=0, row=4, sticky=tk.NSEW)
        popButtonAbort.grid(column=0, row=5, sticky=tk.NSEW)

        # global pixel
        # popButtonPay.config(image=pixel, compound="c", font=("Verdana", 15), height=15)

        popButtonPay.config(font=("Verdana", 20))

        popPay.columnconfigure(0, weight=1)
        popPay.rowconfigure(0, weight=1)
        popPay.rowconfigure(1, weight=1)
        popPay.rowconfigure(2, weight=1)

        popPay.mainloop()

# ---------------------------------------------- #
# ------------- Manage Order View -------------- #
# ---------------------------------------------- #

def displayOrder():
    orders = widgets.totalTreeViewItems.get_children()
    if orders != '()':
        for order in orders:
            widgets.totalTreeViewItems.delete(order)
    for item in selectedItems:
        widgets.totalTreeViewItems.insert("", "end", text=item[0], values=("%.2f€" % item[1], str(selectedItems[item]), "%.2f€" % (item[1]*selectedItems[item])), tags=item)
    updateTotal()

def updateTotal():
    global totalSV
    total = 0
    for item in selectedItems:
        total += item[1]*selectedItems[item]
    totalSV.set("Summe: %.2f €" % total)

# -------------------------------------------------------------------------------------------- #
# ----------------------------------- Create Layout ------------------------------------------ #
# -------------------------------------------------------------------------------------------- #

pixel = tk.PhotoImage(width=1, height=1)


style = ttk.Style()
style.configure("Treeview", font=("Verdana", 20))

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
assets.teamimageOn  = {}
assets.teamimageOff = {}
assets.teamimageResizeOn  = {}
assets.teamimageResizeOff = {}

f = open("teams.txt", "r")
SETTINGS.teamList = f.readlines()
f.close()
SETTINGS.teamList = list(map(str.strip, SETTINGS.teamList))

# load team images and store
for i in range(len(SETTINGS.teamList)):
    assets.teamimageOn[i] = Image.open("Logo_" + SETTINGS.teamList[i] + "_On.gif")
    assets.teamimageOff[i] = Image.open("Logo_" + SETTINGS.teamList[i] + "_Off.gif")

# create buttons
for i in range(len(SETTINGS.teamList)):
    widgets.teambuttons[i] = tk.Radiobutton(frames.teams, command=partial(onSelectTeam, SETTINGS.teamList[i]), value=SETTINGS.teamList[i], variable=selectedTeam)
    widgets.teambuttons[i].configure(text=SETTINGS.teamList[i], indicatoron=tk.TRUE, bg="orange", height=1, width=1, image=pixel, compound="c")
    widgets.teambuttons[i].grid(row=i // 3, column=i % 3, sticky=tk.NSEW, padx=5, pady=5)

# configure team frame so that contents scale
for col_num in range(frames.teams.grid_size()[0]):
    frames.teams.columnconfigure(col_num,weight=1)
for row_num in range(frames.teams.grid_size()[1]):
    frames.teams.rowconfigure(row_num,weight=1)

def ResizeTeamImages():
    print("resize team image called")
    root.update_idletasks()
    frames.teams.update()
    for i in range(len(SETTINGS.teamList)):
        teamimagesize = min(widgets.teambuttons[i].winfo_height(), widgets.teambuttons[i].winfo_width())
        # resize images
        assets.teamimageResizeOn[i] = ImageTk.PhotoImage(assets.teamimageOn[i].resize( (teamimagesize, teamimagesize), resample=Image.LANCZOS))
        assets.teamimageResizeOff[i] = ImageTk.PhotoImage(assets.teamimageOff[i].resize( (teamimagesize, teamimagesize), resample=Image.LANCZOS))
        # assign images
        widgets.teambuttons[i].config(image=assets.teamimageResizeOn[i])
        widgets.teambuttons[i].config(selectimage=assets.teamimageResizeOff[i])

ResizeTeamImages()

#frames.teams.bind("<Configure>", ResizeTeamImages())

# ---------------------------------------------- #
# -------------Create Players Treeview --------- #
# ---------------------------------------------- #


widgets.playerTreeView = ttk.Treeview(frames.players)
widgets.playerTreeView["columns"]=("one")
widgets.playerTreeView.heading("#0",  text="Spieler")
widgets.playerTreeView.heading("one", text="B", anchor=tk.W)
widgets.playerTreeView.column("#0", width=100, stretch=1)
widgets.playerTreeView.column("one", width=20, stretch=1)

widgets.playerButtonAdd = tk.Button(frames.players, text="Spieler\n hinzufügen", command=addPlayer)
widgets.playerButtonRename = tk.Button(frames.players, text="Spieler\n umbenennen", command=renamePlayer)
widgets.playerButtonPay = tk.Button(frames.players, text="Spieler\n abrechnen", command=popupPay)

widgets.playerButtonAdd.configure(image=pixel, font=("Courier", 20), height=40, compound="c")
widgets.playerButtonPay.configure(image=pixel, font=("Courier", 20), height=40, compound="c")
widgets.playerButtonRename.configure(image=pixel, font=("Courier", 20), height=40, compound="c")

widgets.playerTreeView.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)
widgets.playerButtonAdd.grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=10)
widgets.playerButtonPay.grid(row=2, column=0, sticky=tk.NSEW, padx=10, pady=10)
widgets.playerButtonRename.grid(row=3, column=0, sticky=tk.NSEW, padx=10, pady=10)

frames.players.rowconfigure(0,weight=1)
frames.players.columnconfigure(0,weight=1)

# ---------------------------------------------- #
# -------------Create Item Frames -------------- #
# ---------------------------------------------- #

SETTINGS.items = SimpleNamespace()
SETTINGS.items.name = []
SETTINGS.items.price = []
SETTINGS.items.category = []

frames.itemcategories = {}
widgets.itembutton = {}

# read food file
f = open("food.txt", "r")
foodList = f.readlines()
f.close()

for i in range(len(foodList)):
    [name, price, category] = foodList[i].strip().split(";")
    SETTINGS.items.name.append(name)
    SETTINGS.items.price.append(price)
    SETTINGS.items.category.append(int(category))

# create category containers
for i in range(len(set(SETTINGS.items.category))):
    #create frames and put onto grid
    frames.itemcategories[i] = tk.Frame(frames.items, bg="red")
    frames.itemcategories[i].grid(column=0, row=i, sticky=tk.NSEW, padx=10, pady=10)
    #calc needed weight for each frame
    rowweight = math.ceil(SETTINGS.items.category.count(sorted(set(SETTINGS.items.category))[i]) / 3)
    #configure with correct weight
    frames.items.rowconfigure(i,weight=rowweight)
    frames.items.columnconfigure(0,weight=1)

# create item buttons
for i in range(len(SETTINGS.items.name)):
    widgets.itembutton[i] = tk.Button(frames.itemcategories[SETTINGS.items.category[i]], command=partial(onClickItem, SETTINGS.items.name[i], float(SETTINGS.items.price[i])))
    buttontext = SETTINGS.items.name[i] + "\n" + str(SETTINGS.items.price[i]) + "€"
    widgets.itembutton[i].config(image=pixel, compound="c", text=buttontext, font=("Courier", 15), width=1)
    # figure out position of button widget in current category frame
    currentint = 0
    for j in range(i):
        if SETTINGS.items.category[j] == SETTINGS.items.category[i]:
            currentint = currentint +1
    # place widget in category frame
    widgets.itembutton[i].grid(row=(currentint)//3, column=(currentint)%3, sticky=tk.NSEW, pady=10, padx=10)

for i in range(len(frames.itemcategories)):
    for j in range(frames.itemcategories[i].grid_size()[0]):
        frames.itemcategories[i].columnconfigure(j, weight=1)
    for j in range(frames.itemcategories[i].grid_size()[1]):
        frames.itemcategories[i].rowconfigure(j, weight=1)

# ---------------------------------------------- #
# -------------fill total frame ---------------- #
# ---------------------------------------------- #

totalSV = tk.StringVar()
totalSV.set("0.00 €")

widgets.totalTreeViewItems = ttk.Treeview(frames.total)
widgets.totalTreeViewItems["columns"]=("Preis", "Anzahl", "Gesamt")
widgets.totalTreeViewItems.heading("#0",  text="Bestellung")
widgets.totalTreeViewItems.heading("Preis", text="Preis", anchor=tk.W)
widgets.totalTreeViewItems.heading("Anzahl", text="Anzahl", anchor=tk.W)
widgets.totalTreeViewItems.heading("Gesamt", text="Gesamt")
widgets.totalTreeViewItems.column('#0', width=100, stretch=1)
widgets.totalTreeViewItems.column('Preis', width=20, stretch=1)
widgets.totalTreeViewItems.column('Anzahl', width=10, stretch=1)
widgets.totalTreeViewItems.column('Gesamt', width=20, stretch=1)
widgets.totalTreeViewItems.bind('<<TreeviewSelect>>', onSelectOrder)

widgets.totalLabelSum = tk.Label(frames.total, textvariable=totalSV)
widgets.totalLabelSum.configure(image=pixel, font=("Courier", 30), relief="sunken", height=70, compound="c")

widgets.totalButtonClear = tk.Button(frames.total, text="Auswahl löschen", command=deleteOrder)
widgets.totalButtonStorno = tk.Button(frames.total, text="Buchung stornieren", command=stornoOrder)
widgets.totalButtonConfirm = tk.Button(frames.total, text="Buchung bestätigen", command=confirmOrder)

widgets.totalButtonClear.configure(image=pixel, compound="c", font=("Courier", 15), height=30)
widgets.totalButtonStorno.configure(image=pixel, compound="c", font=("Courier", 15), height=30)
widgets.totalButtonConfirm.configure(image=pixel, compound="c", font=("Courier", 30), height=70)

widgets.totalTreeViewItems.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)
widgets.totalLabelSum.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
widgets.totalButtonClear.grid(column=0, row=2, sticky=tk.NSEW, padx=10, pady=10)
widgets.totalButtonStorno.grid(column=0, row=3, sticky=tk.NSEW, padx=10, pady=10)
widgets.totalButtonConfirm.grid(column=0, row=4, sticky=tk.NSEW, padx=10, pady=10)

frames.total.rowconfigure(0,weight=1)
frames.total.columnconfigure(0,weight=1)

# ---------------------------------------------- #
# -------------fill status bar ----------------- #
# ---------------------------------------------- #

widgets.statusbarButtonExit = tk.Button(frames.statusbar, text="Kasse Beenden", bg="yellow")
widgets.statusbarButtonExit.pack(side="left")

# -------------------------------------------------------------------------------------------- #
# ----------------------------------- Runtime ------------------------------------------------ #
# -------------------------------------------------------------------------------------------- #

# create Player Table
create_table_players = "CREATE TABLE IF NOT EXISTS players(id integer primary key autoincrement, player_name text, team_name text, is_payed integer default 0)"
runQuery(create_table_players)

# create Order Table
create_table_order = "CREATE TABLE IF NOT EXISTS purchases(id integer primary key autoincrement, player_id integer, item_name text, item_quantity integer, price numeric, payed integer default 0)"
runQuery(create_table_order)

root.mainloop()