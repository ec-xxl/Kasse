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


def closeRegister():
    root.destroy()
# ---------------------------------------------- #
# ------------- Selection Actions -------------- #
# ---------------------------------------------- #

def onSelectTeam(team):
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


def displayPlayers(team):
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
        if popEntry.get():
            team = getSelectedTeam()
            player = popEntry.get()  # This is the text you may want to use later
            insert_player = "INSERT INTO players (player_name, team_name) VALUES (?, ?)"    # SQL-String
            runQuery(insert_player, (player, team))     # add to Database
            displayPlayers(team)    # add to Listbox
            popupPlayerAdd.destroy()

    if getSelectedTeam():
        # create popup window
        popupPlayerAdd = tk.Tk()
        popupPlayerAdd.title("Spieler hinzufügen")
        # popupPlayerAdd.overrideredirect(1)
        popupPlayerAdd.attributes("-topmost", True)  # Always keep window on top of others
        popupPlayerAdd.geometry("%dx%d+%d+%d" % (400, 200, root.winfo_screenwidth() / 2 - 200, root.winfo_screenheight() / 2 - 100))
        popupPlayerAdd.focus_set()
        # create widgets
        popLabel = tk.Label(popupPlayerAdd, text="Spieler hinzufügen")
        popEntry = tk.Entry(popupPlayerAdd, justify='center', font=("Verdana",20))
        popButtonAbort = tk.Button(popupPlayerAdd, text="Abbrechen", command= lambda: popupPlayerAdd.destroy(), width=1)
        popButtonOK = tk.Button(popupPlayerAdd, text="OK", font=("Verdana", 20), command=lambda: callback(), width=1)
        # place on grid
        popLabel.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popEntry.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popButtonAbort.grid(row=2, column=0, sticky=tk.NSEW, padx=10, pady=10)
        popButtonOK.grid(row=2, column=1, sticky=tk.NSEW, padx=10, pady=10)
        # configure grid
        popupPlayerAdd.rowconfigure(0, weight=1)
        popupPlayerAdd.rowconfigure(1, weight=1)
        popupPlayerAdd.rowconfigure(2, weight=1)
        popupPlayerAdd.columnconfigure(0, weight=1)
        popupPlayerAdd.columnconfigure(1, weight=1)
        #
        popEntry.focus()
        popupPlayerAdd.bind("<Return>", callback)
        popupPlayerAdd.mainloop()
    else:
        popupError("Bitte ein Team auswählen")

def renamePlayer():
    def callback(event=None):
        if popEntry.get():
            team = getSelectedTeam()
            playerID = getSelectedPlayerID()
            player_name = popEntry.get()  # Entry of new name
            update_player = "UPDATE players SET player_name = ? WHERE id = ?"    # SQL-String
            runQuery(update_player, (player_name, playerID))     # add to Database
            displayPlayers(team)    # add to Listbox
            popup.destroy()

    if getSelectedPlayerID():
        # create popup window
        popupPlayerRename = tk.Tk()
        popupPlayerRename.title("Spieler umbenennen")
        # popupPlayerRename.overrideredirect(1)
        popupPlayerRename.attributes("-topmost", True)  # Always keep window on top of others
        popupPlayerRename.geometry("%dx%d+%d+%d" % (400, 200, root.winfo_screenwidth() / 2 - 200, root.winfo_screenheight() / 2 - 100))
        popupPlayerRename.focus_set()
        # create widgets
        popLabel = tk.Label(popupPlayerRename, text="Spieler '' umbenennen")
        popEntry = tk.Entry(popupPlayerRename, justify='center', font=("Verdana",20))
        popButtonAbort = tk.Button(popupPlayerRename, text="Abbrechen", command= lambda: popupPlayerRename.destroy(), width=1)
        popButtonOK = tk.Button(popupPlayerRename, text="OK", font=("Verdana",20), command=lambda: callback(), width=1)
        # place on grid
        popLabel.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popEntry.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popButtonAbort.grid(row=2, column=0, sticky=tk.NSEW, padx=10, pady=10)
        popButtonOK.grid(row=2, column=1, sticky=tk.NSEW, padx=10, pady=10)
        # configure grid
        popupPlayerRename.rowconfigure(0, weight=1)
        popupPlayerRename.rowconfigure(1, weight=1)
        popupPlayerRename.rowconfigure(2, weight=1)
        popupPlayerRename.columnconfigure(0, weight=1)
        popupPlayerRename.columnconfigure(1, weight=1)
        #
        popEntry.focus()
        popupPlayerRename.bind("<Return>", callback)
        popupPlayerRename.mainloop()
    else:
        popupError("Bitte einen Spieler auswählen")

def confirmOrder():
    global selectedItems
    player_id = getSelectedPlayerID()
    if player_id:
        for item in selectedItems:
            insert_order = "INSERT INTO purchases (player_id, item_name, price, item_quantity, is_payed) VALUES (?, ?, ?, ?, ?)"
            data = (player_id, item[0], item[1], selectedItems[item], 0)
            runQuery(insert_order, data)
        set_payed = "UPDATE players SET is_payed=0 WHERE id = ?"
        runQuery(set_payed, (player_id,))
        selectedItems = {}
        selectedTeam.set("")        # Unselect Team
        displayPlayers("")          # Show empty Player List
        displayOrder()

def stornoOrder():
    global selectedItems
    player_id = getSelectedPlayerID()
    if player_id:
        for item in selectedItems:
            insert_order = "INSERT INTO purchases (player_id, item_name, price, item_quantity, is_payed) VALUES (?, ?, ?, ?, ?)"
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
        popPay.title("Bezahlen")
        # popPay.overrideredirect(1) # Remove shadow & drag bar. Note: Must be used before wm calls otherwise these will be removed.
        popPay.attributes("-topmost", True)
        popPay.geometry("%dx%d+%d+%d" % (400, 400, root.winfo_screenwidth() / 2 - 200, root.winfo_screenheight() / 2 - 200))
        popPay.call("wm", "attributes", ".", "-topmost", "true") # Always keep window on top of others
        # create treeview
        widgets.payTreeView = ttk.Treeview(popPay)
        widgets.payTreeView["columns"] = ("Preis", "Anzahl", "Gesamt", "Bezahlt")
        widgets.payTreeView.heading("#0", text="Bestellung")
        widgets.payTreeView.heading("Preis", text="Preis", anchor=tk.W)
        widgets.payTreeView.heading("Anzahl", text="Anzahl", anchor=tk.W)
        widgets.payTreeView.heading("Gesamt", text="Gesamt")
        widgets.payTreeView.heading("Bezahlt", text="Bezahlt")
        widgets.payTreeView.column('#0', width=100, stretch=1)
        widgets.payTreeView.column('Preis', width=20, stretch=1)
        widgets.payTreeView.column('Anzahl', width=10, stretch=1)
        widgets.payTreeView.column('Gesamt', width=20, stretch=1)
        widgets.payTreeView.column('Bezahlt', width=10, stretch=1)
        # sum up purchases
        select_purchases = "SELECT item_name, price, SUM(item_quantity), is_payed FROM purchases WHERE player_id = ? GROUP BY item_name, price, is_payed"
        purchases = runQuery(select_purchases, (playerID,), receive=tk.TRUE)
        total_payed = 0
        total_due = 0
        for purchase in purchases:
            widgets.payTreeView.insert("", "end", text=purchase[0], values=("%.2f€" % purchase[1], purchase[2], "%.2f€" % (purchase[1]*purchase[2]), "x" if purchase[3] else ""))
            total_due += 0 if purchase[3] else (purchase[1]*purchase[2])
            total_payed += (purchase[1]*purchase[2]) if purchase[3] else 0
        total = total_due+total_payed

        def deduction():
            pay_purchases = "UPDATE purchases SET is_payed = 1 WHERE player_id = ?"
            runQuery(pay_purchases, (playerID,))
            set_payed = "UPDATE players SET is_payed = 1 WHERE id = ?"
            runQuery(set_payed, (playerID,))
            displayPlayers(getSelectedTeam())
            popPay.destroy()

        # create labels
        popLabelDescTotal = tk.Label(popPay, text="Summe der Einkäufe:", anchor="e", width=1)
        popLabelDescPaid = tk.Label(popPay, text="Bisher bezahlt:", anchor="e", width=1)
        popLabelDescDue = tk.Label(popPay, text="Übrig:", anchor="e", font=(None, 15, "bold"), width=1)
        popLabelTotal = tk.Label(popPay, text="%.2f€" % total, anchor="w", width=1)
        popLabelPaid = tk.Label(popPay, text="%.2f€" % total_payed, anchor="w", width=1)
        popLabelDue = tk.Label(popPay, text="%.2f€" % total_due, anchor="w", font=(None, 15, "bold"), width=1)

        # create buttons
        popButtonPay = tk.Button(popPay, text="Bezahlen", command=deduction, width=1)
        popButtonAbort = tk.Button(popPay, text="Abbrechen", command=lambda: popPay.destroy(), width=1)

        # place widgets on grid
        widgets.payTreeView.grid(column=0,row=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popLabelDescTotal.grid(column=0, row=1, sticky=tk.EW)
        popLabelDescPaid.grid(column=0, row=2, sticky=tk.EW)
        popLabelDescDue.grid(column=0, row=3, sticky=tk.EW)
        popLabelTotal.grid(column=1, row=1, sticky=tk.EW)
        popLabelPaid.grid(column=1, row=2, sticky=tk.EW)
        popLabelDue.grid(column=1, row=3, sticky=tk.EW)
        popButtonAbort.grid(column=0, row=4, sticky=tk.NSEW, padx=10, pady=10)
        popButtonPay.grid(column=1, row=4, sticky=tk.NSEW, padx=10, pady=10)

        # global pixel
        # popButtonPay.config(image=pixel, compound="c", font=("Verdana", 15), height=15)

        popButtonPay.config(font=("Verdana", 20))

        popPay.columnconfigure(0, weight=1)
        popPay.columnconfigure(1, weight=1)
        popPay.rowconfigure(0, weight=1)
        popPay.rowconfigure(1, weight=1)
        popPay.rowconfigure(2, weight=1)
        popPay.rowconfigure(3, weight=1)
        popPay.rowconfigure(4, weight=1)

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
style.configure("Treeview", font=("Verdana", 20), rowheight=45)

# ---------------------------------------------- #
# ------------- Create Main Frames ------------- #
# ---------------------------------------------- #

frames.main = tk.Frame(root, bg="red")
frames.statusbar = tk.Frame(root, bg="#DBDF31")

frames.main.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
frames.statusbar.grid(row=1,column=0, sticky=tk.N+tk.S+tk.E+tk.W)

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0, minsize=40)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=0)

# ---------------------------------------------- #
# ------------- Create Subframees -------------- #
# ---------------------------------------------- #

frames.teams = tk.Frame(frames.main, bg="#999999")
frames.players = tk.Frame(frames.main, bg="#FC5252")
frames.items = tk.Frame(frames.main, bg="#5AAE4A")
frames.total = tk.Frame(frames.main, bg="#4A98AE")

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
# ------------- fill team frame ---------------- #
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
    widgets.teambuttons[i].configure(text=SETTINGS.teamList[i], indicatoron=tk.TRUE, bg="#999999", height=1, width=1, image=pixel)
    widgets.teambuttons[i].grid(row=i // 3, column=i % 3, sticky=tk.NSEW, padx=5, pady=5)

# configure team frame so that contents scale
for col_num in range(frames.teams.grid_size()[0]):
    frames.teams.columnconfigure(col_num,weight=1)
for row_num in range(frames.teams.grid_size()[1]):
    frames.teams.rowconfigure(row_num,weight=1)

def ResizeTeamImages():
    # print("resize team image called")
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
# ------------- fill players frame ------------- #
# ---------------------------------------------- #

frames.playerTreeViewFrame = tk.Frame(frames.players, bg="green")

widgets.playerTreeView = ttk.Treeview(frames.playerTreeViewFrame)
widgets.playerTreeView["columns"]=("one")
widgets.playerTreeView.heading("#0",  text="Spieler")
widgets.playerTreeView.heading("one", text="B", anchor=tk.W)
widgets.playerTreeView.column("#0", width=100, stretch=1)
widgets.playerTreeView.column("one", width=20, stretch=1)

widgets.playerTreeViewVSB = ttk.Scrollbar(frames.playerTreeViewFrame,orient="vertical",command=widgets.playerTreeView.yview)
widgets.playerTreeView.configure(yscrollcommand=widgets.playerTreeViewVSB.set)

widgets.playerButtonAdd = tk.Button(frames.players, text="Spieler\n hinzufügen", command=addPlayer)
widgets.playerButtonRename = tk.Button(frames.players, text="Spieler\n umbenennen", command=renamePlayer)
widgets.playerButtonPay = tk.Button(frames.players, text="Spieler\n abrechnen", command=popupPay)

widgets.playerButtonAdd.configure(image=pixel, font=("Verdana", 20), height=40, compound="c", highlightbackground="#973131")
widgets.playerButtonPay.configure(image=pixel, font=("Verdana", 20), height=40, compound="c", highlightbackground="#973131")
widgets.playerButtonRename.configure(image=pixel, font=("Verdana", 20), height=40, compound="c", highlightbackground="#973131")

frames.playerTreeViewFrame.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)
widgets.playerButtonAdd.grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=10)
widgets.playerButtonPay.grid(row=2, column=0, sticky=tk.NSEW, padx=10, pady=10)
widgets.playerButtonRename.grid(row=3, column=0, sticky=tk.NSEW, padx=10, pady=10)

widgets.playerTreeView.pack(fill="both",side="left",expand=tk.TRUE)
widgets.playerTreeViewVSB.pack(fill="both",side="right")

frames.players.rowconfigure(0,weight=1)
frames.players.columnconfigure(0,weight=1)

# ---------------------------------------------- #
# -------------fill item frame ----------------- #
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
    frames.itemcategories[i] = tk.Frame(frames.items, bg="#71C968")
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
    widgets.itembutton[i].config(image=pixel, compound="c", text=buttontext, font=("Verdana", 15), width=1, highlightbackground="#44793E")
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

frames.totalTreeViewFrame = tk.Frame(frames.total, bg="green")

widgets.totalTreeViewItems = ttk.Treeview(frames.totalTreeViewFrame)
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

widgets.totalTreeViewItemsVSB = ttk.Scrollbar(frames.totalTreeViewFrame,orient="vertical",command=widgets.totalTreeViewItems.yview)
widgets.totalTreeViewItems.configure(yscrollcommand=widgets.totalTreeViewItemsVSB.set)

widgets.totalLabelSum = tk.Label(frames.total, textvariable=totalSV)
widgets.totalLabelSum.configure(image=pixel, font=("Verdana", 30), relief="sunken", height=70, compound="c")

widgets.totalButtonClear = tk.Button(frames.total, text="Auswahl löschen", command=deleteOrder, highlightbackground="#307F95")
widgets.totalButtonStorno = tk.Button(frames.total, text="Buchung stornieren", command=stornoOrder, highlightbackground="#307F95")
widgets.totalButtonConfirm = tk.Button(frames.total, text="Buchung bestätigen", command=confirmOrder, highlightbackground="#307F95")

widgets.totalButtonClear.configure(image=pixel, compound="c", font=("Verdana", 15), height=30)
widgets.totalButtonStorno.configure(image=pixel, compound="c", font=("Verdana", 15), height=30)
widgets.totalButtonConfirm.configure(image=pixel, compound="c", font=("Verdana", 30), height=70)

frames.totalTreeViewFrame.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)
widgets.totalLabelSum.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
widgets.totalButtonClear.grid(column=0, row=2, sticky=tk.NSEW, padx=10, pady=10)
widgets.totalButtonStorno.grid(column=0, row=3, sticky=tk.NSEW, padx=10, pady=10)
widgets.totalButtonConfirm.grid(column=0, row=4, sticky=tk.NSEW, padx=10, pady=10)

widgets.totalTreeViewItems.pack(fill="both",side="left",expand=tk.TRUE)
widgets.totalTreeViewItemsVSB.pack(fill="both",side="right")

frames.total.rowconfigure(0,weight=1)
frames.total.columnconfigure(0,weight=1)

# ---------------------------------------------- #
# -------------fill status bar ----------------- #
# ---------------------------------------------- #

widgets.statusbarButtonExit = tk.Button(frames.statusbar, text="Kasse Beenden", bg="yellow", command=closeRegister, highlightbackground="#DBDF31")
widgets.statusbarButtonExit.grid(row=1, column=1, padx=10, pady=10)

# -------------------------------------------------------------------------------------------- #
# ----------------------------------- Runtime ------------------------------------------------ #
# -------------------------------------------------------------------------------------------- #

# create Player Table
create_table_players = "CREATE TABLE IF NOT EXISTS players(id integer primary key autoincrement, player_name text, team_name text, is_payed integer default 0)"
runQuery(create_table_players)

# create Order Table
create_table_order = "CREATE TABLE IF NOT EXISTS purchases(id integer primary key autoincrement, player_id integer, item_name text, item_quantity integer, price numeric, is_payed integer default 0)"
runQuery(create_table_order)

root.mainloop()