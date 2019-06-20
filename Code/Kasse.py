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


# ---------------------------------------------- #
# ------------- Create Namespaces -------------- #
# ---------------------------------------------- #

frames = SimpleNamespace()
widgets = SimpleNamespace()
SETTINGS = SimpleNamespace()
selection = SimpleNamespace()

# ---------------------------------------------- #
# ------------- Create root window ------------- #
# ---------------------------------------------- #

root = tk.Tk()
# root.overrideredirect(1) # Remove shadow & drag bar. Note: Must be used before wm calls otherwise these will be removed.
# root.call("wm", "attributes", ".", "-topmost", "true") # Always keep window on top of others
root.geometry("%dx%d+0+0" % (root.winfo_screenwidth(), root.winfo_screenheight()) )
# root.call("wm", "attributes", ".", "-fullscreen", "true") # Fullscreen mode
# root.tk.call("::tk::unsupported::MacWindowStyle", "style", root._w, "plain", "none")
# root.focus_set()

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
    popupRoot.after(2000, lambda: popupRoot.destroy())          # Time in Miliseconds 2000 = 2 seconds
    popupButton = tk.Button(popupRoot, text=s, font=("Verdana", 12), bg="yellow", command=lambda: popupRoot.destroy())
    popupButton.pack()
    popupRoot.geometry('400x50+700+500')
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
    widgets.playerlistbox.listbox.delete(0, tk.END)
    players = get_players(team)
    global displayedPlayers
    displayedPlayers = players
    for player_id, player in players:
        widgets.playerlistbox.listbox.insert(tk.END, player)

# ---------------------------------------------- #
# ------------- Info get ----------------------- #
# ---------------------------------------------- #

def get_players(team: str):
    select_player = "SELECT id, player_name FROM players WHERE team_name = ?"
    players = runQuery(select_player, (team,), receive=tk.TRUE)
    return players

def getSelectedTeam():
    return selectedTeam.get()

def getSelectedPlayerID():
    if widgets.playerlistbox.listbox.curselection():
        pos = widgets.playerlistbox.listbox.curselection()[0]
        return displayedPlayers[pos][0]
    else:
        popupError("Bitte einen Spieler auswählen")

# ---------------------------------------------- #
# ------------- Button Actions ----------------- #
# ---------------------------------------------- #

def add_player():
    def callback(event=None):
        if e.get():
            player = e.get()  # This is the text you may want to use later
            insert_player = "INSERT INTO players (player_name, team_name) VALUES (?, ?)"    # SQL-String
            runQuery(insert_player, (player, team))     # add to Database
            displayPlayers(team)    # add to Listbox
            popup.destroy()

    if getSelectedTeam():
        team = getSelectedTeam()
        popup = tk.Tk()
        popup.attributes("-topmost", True)
        e = tk.Entry(popup)
        e.pack()
        e.focus()
        popButton = tk.Button(popup, text="OK", width=10, command=callback)
        popButton.pack()
        popup.bind("<Return>", callback)
        popup.mainloop()
    else:
        popupError("Bitte ein Team auswählen")

def confirmOrder():
    global selectedItems
    player_id = getSelectedPlayerID()
    if player_id:
        for item in selectedItems:
            insert_order = "INSERT INTO purchases (player_id, item_name, price, item_quantity, payed) VALUES (?, ?, ?, ?, ?)"
            data = (player_id, item[0], item[1], selectedItems[item], 0)
            runQuery(insert_order, data)
        selectedItems = {}
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
        displayOrder()

def deleteOrder():
    global selectedItems
    selectedItems = collections.OrderedDict()
    displayOrder()

def popupPay():
    playerID = getSelectedPlayerID()
    if playerID:
        popPay = tk.Tk()
        popPay.attributes("-topmost", True)
        listbox_purchases = tk.Listbox(popPay)
        listbox_purchases.grid(column=0, row=0)

        select_purchases = "SELECT item_name, price, SUM(item_quantity) FROM purchases WHERE player_id = ? AND payed = 0 GROUP BY item_name, price"
        purchases = runQuery(select_purchases, (playerID,), receive=tk.TRUE)
        total = 0
        for purchase in purchases:
            listbox_purchases.insert(tk.END, purchase[0]+" "+str(purchase[1])+"€ x "+str(purchase[2]))
            total += purchase[1]*purchase[2]

        tk.Label(popPay, text="Summe der Einkäufe %.2f€" % total).grid(column=0, row=1)
        def deduction():
            pay_purchases = "UPDATE purchases SET payed = 1 WHERE player_id = ?"
            runQuery(pay_purchases, (playerID,))
            popPay.destroy()


        popButton = tk.Button(popPay, text="Abrechnen", width=10, command=deduction)
        popButton.grid(column=0, row=2)
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

f = open("teams.txt", "r")
SETTINGS.teamList = f.readlines()
f.close()
SETTINGS.teamList = list(map(str.strip, SETTINGS.teamList))

SETTINGS.teamimagesize = int(root.winfo_screenwidth() / 7 * 2 / 3)

for i in range(len(SETTINGS.teamList)):
    # create buttons
    widgets.teambuttons[i] = tk.Radiobutton(frames.teams, text=SETTINGS.teamList[i], command=partial(onSelectTeam, SETTINGS.teamList[i]), value=SETTINGS.teamList[i], variable=selectedTeam, indicatoron=tk.FALSE, bg="orange")
    widgets.teambuttons[i].grid(row=i // 3, column=i % 3, sticky=tk.NSEW, padx=0, pady=0)
    # load 'on' image
    img = Image.open("Logo_"+SETTINGS.teamList[i]+"_On.gif")
    img = img.resize((SETTINGS.teamimagesize,SETTINGS.teamimagesize), resample=Image.LANCZOS)
    widgets.teamimageson[i] =  ImageTk.PhotoImage(img)
    widgets.teambuttons[i].config(image=widgets.teamimageson[i])
    # load 'off' image
    img = Image.open("Logo_"+SETTINGS.teamList[i]+"_Off.gif")
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

widgets.playerAddButton = tk.Button(frames.players, text="Spieler hinzufügen", command=add_player)
widgets.playerAddButton.grid(row=1, column=0, sticky=tk.NSEW)

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
    frames.itemcategories[i] = tk.Frame(frames.items, bg="red")
    frames.itemcategories[i].grid(column=0, row=i, sticky=tk.NSEW, padx=10, pady=10)

    rowweight = math.ceil(SETTINGS.items.category.count(sorted(set(SETTINGS.items.category))[i]) / 3)

    frames.items.rowconfigure(i,weight=rowweight)
    frames.items.columnconfigure(0,weight=1)

for i in range(len(SETTINGS.items.name)):
    # create item button
    buttontext = SETTINGS.items.name[i] + "\n" + str(SETTINGS.items.price[i]) + "€"
    widgets.itembutton[i] = tk.Button(frames.itemcategories[SETTINGS.items.category[i]], text=buttontext, command=partial(onClickItem, SETTINGS.items.name[i], float(SETTINGS.items.price[i])), font=("Courier", 20))
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
widgets.totalTreeViewItems.heading("0",  text="Bestellung")
widgets.totalTreeViewItems.heading("Preis", text="Preis", anchor=tk.W)
widgets.totalTreeViewItems.heading("Anzahl", text="Anzahl", anchor=tk.W)
widgets.totalTreeViewItems.bind('<<TreeviewSelect>>', onSelectOrder)

widgets.totalLabelSum = tk.Label(frames.total, textvariable=totalSV)

widgets.totalButtonPay = tk.Button(frames.total, text="Spieler abrechnen", command=popupPay)
widgets.totalButtonStorno = tk.Button(frames.total, text="Buchung stornieren", command=stornoOrder)
widgets.totalButtonClear = tk.Button(frames.total, text="Auswahl löschen", command=deleteOrder)
widgets.totalButtonConfirm = tk.Button(frames.total, text="Buchung bestätigen", command=confirmOrder)

widgets.totalTreeViewItems.grid(column=0, row=0, sticky=tk.NSEW)
widgets.totalLabelSum.grid(column=0, row=1, sticky=tk.NSEW)
widgets.totalButtonPay.grid(column=0, row=2, sticky=tk.NSEW)
widgets.totalButtonStorno.grid(column=0, row=3, sticky=tk.NSEW)
widgets.totalButtonClear.grid(column=0, row=4, sticky=tk.NSEW)
widgets.totalButtonConfirm.grid(column=0, row=5, sticky=tk.NSEW)

frames.total.rowconfigure(0,weight=1)
frames.total.columnconfigure(0,weight=1)

# -------------------------------------------------------------------------------------------- #
# ----------------------------------- Runtime ------------------------------------------------ #
# -------------------------------------------------------------------------------------------- #

# create Player Table
create_table_players = "CREATE TABLE IF NOT EXISTS players(id integer primary key autoincrement, player_name text, team_name text)"
runQuery(create_table_players)

# create Order Table
create_table_order = "CREATE TABLE IF NOT EXISTS purchases(id integer primary key autoincrement, player_id integer, item_name text, item_quantity integer, price numeric, payed integer default 0)"
runQuery(create_table_order)

root.mainloop()