# -*- coding: UTF-8 -*-
import collections
import time
import csv

import tkinter as tk
# from time import strftime
from tkinter import ttk
from datetime import datetime

import sqlite3
import math
from functools import partial
from types import SimpleNamespace

import PIL as PIL
from PIL import Image
from PIL import ImageTk

import platform

# TODO
# - [] Info - field for every player
# - [] ERROR - CRITICAL - cannot add multiples of the same item!!!!

# ERROR Linux
# "overridedirect true" is needed for popups created with "toplevel" if popups
# are to stay above a full-screen main window

# if the main window (created with "tk.Tk" and instantiated with "mainloop()") is NOT full-screen,
# "Toplevel" popups don't need to be either

# ERROR MacOS

# Error
# after ending "player rename" or "player add" button with keypress "OK" the next time the window is opened
# no focus into the "entry" field can be achieved

# ---------------------------------------------- #
# ------------- Create root window ------------- #
# ---------------------------------------------- #

root = tk.Tk()
root.title("Kassensystem Südsee Cup")
if platform.system() == "Darwin":
    # root.overrideredirect(1) # Remove shadow & drag bar.
    # Note: Must be used before wm calls otherwise these will be removed.

    # root.call("wm", "attributes", ".", "-topmost", "true") # Always keep window on top of others
    # root.geometry("%dx%d+0+0" % (root.winfo_screenwidth(), root.winfo_screenheight()) )
    root.geometry("%dx%d+%d+%d" % (1280, 800, root.winfo_screenwidth()/2 - 640, root.winfo_screenheight()/2 - 400))
    # root.call("wm", "attributes", ".", "-fullscreen", "true") # Fullscreen mode
    # root.tk.call("::tk::unsupported::MacWindowStyle", "style", root._w, "plain", "none")
    root.focus_set()
else:
    # root.geometry("%dx%d+0+0" % (root.winfo_screenwidth(), root.winfo_screenheight()) )
    root.geometry("%dx%d+0+0" % (1280, 800))
    root.call("wm", "attributes", ".", "-fullscreen", "true")  # Fullscreen mode
    root.focus_set()

# ---------------------------------------------- #
# ------------- Create Namespaces -------------- #
# ---------------------------------------------- #

frames = SimpleNamespace()
widgets = SimpleNamespace()
assets = SimpleNamespace()
settings = SimpleNamespace()

# ---------------------------------------------- #
# ------------- global variables --------------- #
# ---------------------------------------------- #

selectedTeam = tk.StringVar()
displayedPlayers = []
selectedItems = collections.OrderedDict()

totalSV = tk.StringVar()
totalSV.set("Summe:\n0.00 €")

# -------------------------------------------------------------------------------------------- #
# ----------------------------------- Functions ---------------------------------------------- #
# -------------------------------------------------------------------------------------------- #

# ---------------------------------------------- #
# ------------- General Popups ----------------- #
# ---------------------------------------------- #


# show error message
def popupNotification(parent, s, t, c):
    # create popup window
    popupRoot = tk.Toplevel()
    # create label
    popupWidgetLabelMsg = tk.Label(popupRoot, text=s, font=("Verdana", 20), bg=c)
    popupWidgetLabelMsg.pack(expand=1, fill="both")
    # bind
    popupRoot.after(t, lambda: popupRoot.destroy())          # Time in Miliseconds 1000 = 1 seconds
    # configure popup window
    popupRoot.title("!")
    # popupRoot.overrideredirect(1)
    popupRoot.wm_attributes('-type', 'splash')
    popupRoot.attributes("-topmost", True)  # Always keep window on top of others
    popupRoot.focus_set()
    # popupRoot.grab_set() # make this the only accessible window
    popupRoot.geometry("%dx%d+%d+%d" % (600, 100, root.winfo_screenwidth()/2 - 300, root.winfo_screenheight()/2 - 50))
    # make parent window wait
    # parent.wait_window(popupRoot)


def popupQuestionYESNO(parent, message, title, colour):
    popupReturnVar = tk.IntVar()

    def setAnswer(value):
        popupReturnVar.set(value)
        popupRoot.destroy()

    # create popup window
    popupRoot = tk.Toplevel(background=colour)
    # create widgets
    popupWidgetLabelMsg = tk.Label(popupRoot, text=message)
    popupWidgetButtonNo = tk.Button(popupRoot, text="Nein", command=lambda *args: setAnswer(0))
    popupWidgetButtonYes = tk.Button(popupRoot, text="Ja", command=lambda *args: setAnswer(1))
    # configure widgets
    popupPixel = tk.PhotoImage(width=1, height=1)
    popupWidgetLabelMsg.configure(image=pixel, compound="center", font=("Verdana", 20), width=1, height=1, highlightbackground=colour, background=colour)
    popupWidgetButtonNo.configure(image=pixel, compound="center", font=("Verdana", 20), width=1, height=1, highlightbackground=colour)
    popupWidgetButtonYes.configure(image=pixel, compound="center", font=("Verdana", 20), width=1, height=1, highlightbackground=colour)
    # place widgets
    popupWidgetLabelMsg.grid(column=0, row=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
    popupWidgetButtonNo.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
    popupWidgetButtonYes.grid(column=1, row=1, sticky=tk.NSEW, padx=10, pady=10)
    # configure grid
    popupRoot.columnconfigure(0, weight=1)
    popupRoot.columnconfigure(1, weight=1)
    popupRoot.rowconfigure(0, weight=1)
    popupRoot.rowconfigure(1, weight=1)
    # configure popup window
    popupRoot.title(title)
    # popupRoot.overrideredirect(1)
    popupRoot.wm_attributes('-type', 'splash')
    popupRoot.attributes("-topmost", True)  # Always keep window on top of others
    popupRoot.focus_set()
    popupRoot.grab_set()  # make this the only accessible window
    popupRoot.geometry("%dx%d+%d+%d" % (600, 100, root.winfo_screenwidth()/2 - 300, root.winfo_screenheight()/2 - 50))
    # make parent window wait for desctruction
    parent.wait_window(popupRoot)
    return popupReturnVar.get()

# ---------------------------------------------- #
# ------------- SQLite Database access --------- #
# ---------------------------------------------- #


def runQuery(sql, data=None, receive=False):
    connection = sqlite3.connect("kasse.db")
    cursor = connection.cursor()
    if data:
        cursor.execute(sql, data)
    else:
        cursor.execute(sql)

    if receive:
        return cursor.fetchall()
    else:
        connection.commit()
    connection.close()


# create Player Table
create_table_players = "CREATE TABLE IF NOT EXISTS players(id integer primary key autoincrement, player_name text, team_name text, is_payed integer default 0, info_text text)"
runQuery(create_table_players)

# create Order Table
create_table_order = "CREATE TABLE IF NOT EXISTS purchases(id integer primary key autoincrement, player_id integer, item_name text, item_quantity integer, price numeric, is_payed integer default 0, is_storno integer default 0, purchase_time default current_timestamp)"
runQuery(create_table_order)


def sqlExportDB():
    inpsql3 = sqlite3.connect('kasse.db')
    sql3_cursor = inpsql3.cursor()
    sql3_cursor.execute('SELECT players.player_name, players.team_name, purchases.item_name, purchases.item_quantity, purchases.price, purchases.is_payed FROM purchases join players where purchases.player_id=players.id ORDER BY purchases.is_payed, players.team_name, players.player_name')
    with open('kasse.csv', 'w') as out_csv_file:
        csv_out = csv.writer(out_csv_file)
        # write header
        csv_out.writerow([d[0] for d in sql3_cursor.description])
        # write data
        for result in sql3_cursor:
            csv_out.writerow(result)
    inpsql3.close()
    popupNotification(root, "Export abgeschlossen", 1500, "green")

# ---------------------------------------------- #
# ------------- Selection Actions -------------- #
# ---------------------------------------------- #


def onSelectTeam(team):
    playerDisplay(team)


def onClickItem(name: str, price: float):
    if (name, price) not in selectedItems:
        selectedItems[(name, price)] = 0
    selectedItems[(name, price)] += 1
    orderDisplay()


def onSelectOrder(event):
    global selectedItems
    curItem = widgets.totalTreeViewItems.focus()
    item = widgets.totalTreeViewItems.item(curItem)
    key = (item.get('tags')[0], float(item.get('tags')[1]))
    quantity = selectedItems[key] - 1
    selectedItems[key] = quantity
    if quantity == 0:
        del selectedItems[key]
    orderDisplay()

# ---------------------------------------------- #
# ------------- Info get ----------------------- #
# ---------------------------------------------- #


def getPlayers(team: str):
    select_player = "SELECT id, player_name, is_payed FROM players WHERE team_name = ? ORDER BY player_name"
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
        popupNotification(root, "Bitte einen Spieler auswählen", 1500, "yellow")

# ---------------------------------------------- #
# ------------- Player Button Actions ---------- #
# ---------------------------------------------- #


def playerDisplay(team):
    players = widgets.playerTreeView.get_children()
    if players != '()':
        for player in players:
            widgets.playerTreeView.delete(player)  # delete current entries
    players = getPlayers(team)                     # get players of Team
    global displayedPlayers
    displayedPlayers = players
    for player_id, player, is_payed in players:
        widgets.playerTreeView.insert("", "end", text=player, values=("B" if is_payed else ""), tags=player_id)
    orderUpdateTotal()


def playerAdd(parent):
    def callback(event=None):
        if popupWidgetEntry.get():
            team = getSelectedTeam()
            player = popupWidgetEntry.get()  # This is the text you may want to use later
            insert_player = "INSERT INTO players (player_name, team_name) VALUES (?, ?)"    # SQL-String
            runQuery(insert_player, (player, team))     # add to Database
            playerDisplay(team)    # add to Listbox
            popupRoot.destroy()

    if getSelectedTeam():
        # create popup window
        popupRoot = tk.Toplevel(bg="#C3C3C3")
        # create widgets
        popupWidgetLabel = tk.Label(popupRoot, text="Spieler hinzufügen")
        popupWidgetEntry = tk.Entry(popupRoot)
        popupWidgetButtonAbort = tk.Button(popupRoot, text="Abbrechen", command=lambda: popupRoot.destroy())
        popupWidgetButtonOK = tk.Button(popupRoot, text="OK", command=lambda: callback())
        # configure widgets
        popupPixel = tk.PhotoImage(width=1, height=1)
        popupWidgetLabel.configure(image=popupPixel, compound="center", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetEntry.configure(justify='center', font=(None, 20), width=1)
        popupWidgetButtonAbort.configure(image=popupPixel, compound="center", font=(None, 15), width=1, height=1, highlightbackground="#C3C3C3")
        popupWidgetButtonOK.configure(image=popupPixel, compound="center", font=(None, 20), width=1, height=1, highlightbackground="#C3C3C3")
        # place on grid
        popupWidgetLabel.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetEntry.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetButtonAbort.grid(row=2, column=0, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetButtonOK.grid(row=2, column=1, sticky=tk.NSEW, padx=10, pady=10)
        # configure grid
        popupRoot.rowconfigure(0, weight=1)
        popupRoot.rowconfigure(1, weight=2)
        popupRoot.rowconfigure(2, weight=2)
        popupRoot.columnconfigure(0, weight=1)
        popupRoot.columnconfigure(1, weight=1)
        # configure popup window
        popupRoot.title("Spieler hinzufügen")
        # popupRoot.overrideredirect(1)
        popupRoot.wm_attributes('-type', 'splash')
        popupRoot.attributes("-topmost", True)  # Always keep window on top of others
        popupRoot.focus_set()
        popupRoot.grab_set()  # make this the only accessible window
        popupRoot.geometry("%dx%d+%d+%d" % (400, 200, root.winfo_screenwidth() / 2 - 200, root.winfo_screenheight() / 2 - 100))
        # set focus and callback
        popupWidgetEntry.focus()
        popupRoot.bind("<Return>", callback)
        # make parent window wait
        parent.wait_window(popupRoot)


def playerRename(parent):
    def callback(event=None):
        if popupWidgetEntry.get():
            team = getSelectedTeam()
            playerID = getSelectedPlayerID()
            player_name = popupWidgetEntry.get()  # Entry of new name
            update_player = "UPDATE players SET player_name = ? WHERE id = ?"    # SQL-String
            runQuery(update_player, (player_name, playerID))     # add to Database
            playerDisplay(team)    # add to Listbox
            popupRoot.destroy()

    if getSelectedPlayerID():
        # create popup window
        popupRoot = tk.Toplevel(bg="#C3C3C3")
        # create widgets
        popupWidgetLabel = tk.Label(popupRoot, text="Spieler umbenennen")
        popupWidgetEntry = tk.Entry(popupRoot)
        popupWidgetButtonAbort = tk.Button(popupRoot, text="Abbrechen", command=lambda: popupRoot.destroy())
        popupWidgetButtonOK = tk.Button(popupRoot, text="OK", command=lambda: callback())
        # configure widgets
        popupPixel = tk.PhotoImage(width=1, height=1)
        popupWidgetLabel.configure(image=popupPixel, compound="center", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetEntry.configure(justify='center', font=(None, 20), width=1)
        popupWidgetButtonAbort.configure(image=popupPixel, compound="center", font=(None, 15), width=1, height=1, highlightbackground="#C3C3C3")
        popupWidgetButtonOK.configure(image=popupPixel, compound="center", font=(None, 20), width=1, height=1, highlightbackground="#C3C3C3")
        # place on grid
        popupWidgetLabel.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetEntry.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetButtonAbort.grid(row=2, column=0, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetButtonOK.grid(row=2, column=1, sticky=tk.NSEW, padx=10, pady=10)
        # configure grid
        popupRoot.rowconfigure(0, weight=1)
        popupRoot.rowconfigure(1, weight=2)
        popupRoot.rowconfigure(2, weight=2)
        popupRoot.columnconfigure(0, weight=1)
        popupRoot.columnconfigure(1, weight=1)
        # set focus and callback
        popupWidgetEntry.focus()
        popupRoot.bind("<Return>", callback)
        # configure popup window
        popupRoot.title("Spieler umbenennen")
        # popupRoot.overrideredirect(1)
        popupRoot.wm_attributes('-type', 'splash')
        popupRoot.attributes("-topmost", True)  # Always keep window on top of others
        popupRoot.focus_set()
        popupRoot.grab_set()  # make this the only accessible window
        popupRoot.geometry("%dx%d+%d+%d" % (400, 200, root.winfo_screenwidth() / 2 - 200, root.winfo_screenheight() / 2 - 100))
        # set focus and callback
        popupWidgetEntry.focus()
        popupRoot.bind("<Return>", callback)
        # make parent window wait
        parent.wait_window(popupRoot)


def playerShowSum(parent):
    playerID = getSelectedPlayerID()
    if playerID:
        # create window
        popupRoot = tk.Toplevel(bg="#C3C3C3")
        # create frame for treeView and ScrollBar
        popupWidgetTreeViewFrame = tk.Frame(popupRoot, bg="green")
        # create treeview
        popupWidgetTreeView = ttk.Treeview(popupWidgetTreeViewFrame, height=1)
        popupWidgetTreeView["columns"] = ("1", "2", "3", "4", "5")
        # rename treeview headings
        popupWidgetTreeView.heading("#0", text="Bestellung")
        popupWidgetTreeView.heading("1", text="Preis", anchor="center")
        popupWidgetTreeView.heading("2", text="Anzahl", anchor="center")
        popupWidgetTreeView.heading("3", text="Gesamt", anchor="center")
        popupWidgetTreeView.heading("4", text="Info", anchor="center")
        popupWidgetTreeView.heading("5", text="Zeit", anchor="center")
        # configure treeview columns
        popupWidgetTreeView.column('#0', width=100, stretch=True, anchor="w")
        popupWidgetTreeView.column('1', width=20, stretch=True, anchor="center")
        popupWidgetTreeView.column('2', width=10, stretch=True, anchor="center")
        popupWidgetTreeView.column('3', width=20, stretch=True, anchor="center")
        popupWidgetTreeView.column('4', width=10, stretch=True, anchor="center")
        popupWidgetTreeView.column('5', width=30, stretch=True, anchor="center")
        # scrollbar for tree view
        popupWidgetTreeViewVSB = tk.Scrollbar(popupWidgetTreeViewFrame, orient="vertical", command=popupWidgetTreeView.yview, width=35)
        popupWidgetTreeView.configure(yscrollcommand=popupWidgetTreeViewVSB.set)
        # create widgets
        popupSVTotalSum = tk.StringVar()
        popupSVTotalPaid = tk.StringVar()
        popupSVTotalStorno = tk.StringVar()
        popupSVTotalDue = tk.StringVar()
        popupWidgetDescTotal = tk.Label(popupRoot, text="Summe der Einkäufe:")
        popupWidgetDescPaid = tk.Label(popupRoot, text="Bisher bezahlt:")
        popupWidgetDescStorno = tk.Label(popupRoot, text="Storniert:")
        popupWidgetDescDue = tk.Label(popupRoot, text="Übrig:")
        popupWidgetLabelTotal = tk.Label(popupRoot, textvariable=popupSVTotalSum)
        popupWidgetLabelPaid = tk.Label(popupRoot, textvariable=popupSVTotalPaid)
        popupWidgetLabelStorno = tk.Label(popupRoot, textvariable=popupSVTotalStorno)
        popupWidgetLabelDue = tk.Label(popupRoot, textvariable=popupSVTotalDue)
        popupWidgeButtonOK = tk.Button(popupRoot, text="OK", command=popupRoot.destroy)
        # configure widgets
        popupPixel = tk.PhotoImage(width=1, height=1)
        popupWidgetDescTotal.configure(image=popupPixel, compound="center", anchor="e", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetDescPaid.configure(image=popupPixel, compound="center", anchor="e", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetDescStorno.configure(image=popupPixel, compound="center", anchor="e", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetDescDue.configure(image=popupPixel, compound="center", anchor="e", font=(None, 15, "bold"), width=1, height=1, bg="#C3C3C3")
        popupWidgetLabelTotal.configure(image=popupPixel, compound="center", anchor="w", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetLabelPaid.configure(image=popupPixel, compound="center", anchor="w", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetLabelStorno.configure(image=popupPixel, compound="center", anchor="w", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetLabelDue.configure(image=popupPixel, compound="center", anchor="w", font=(None, 15, "bold"), width=1, height=1, bg="#C3C3C3")
        popupWidgeButtonOK.configure(image=popupPixel, compound="center", font=(None, 15), width=1, height=1, highlightbackground="#C3C3C3")
        # place widgets on grid
        popupWidgetTreeViewFrame.grid(column=0, row=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetDescTotal.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetDescPaid.grid(column=0, row=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetDescStorno.grid(column=0, row=3, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetDescDue.grid(column=0, row=4, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetLabelTotal.grid(column=1, row=1, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetLabelPaid.grid(column=1, row=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetLabelStorno.grid(column=1, row=3, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetLabelDue.grid(column=1, row=4, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgeButtonOK.grid(column=0, row=5, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        # use pack for treeview and vsb
        popupWidgetTreeView.pack(fill="both", side="left", expand=tk.TRUE)
        popupWidgetTreeViewVSB.pack(fill="both", side="right")
        # configure grid
        popupRoot.rowconfigure(0, weight=28)
        popupRoot.rowconfigure(1, weight=2)
        popupRoot.rowconfigure(2, weight=2)
        popupRoot.rowconfigure(3, weight=2)
        popupRoot.rowconfigure(4, weight=2)
        popupRoot.rowconfigure(5, weight=2)
        popupRoot.columnconfigure(0, weight=1)
        popupRoot.columnconfigure(1, weight=1)
        # sum up purchases
        select_purchases = "SELECT item_name, price, item_quantity, is_payed, is_storno, datetime(purchase_time,'localtime') FROM purchases WHERE player_id = ?"  # GROUP BY item_name, price, is_payed, is_storno
        purchases = runQuery(select_purchases, (playerID,), receive=tk.TRUE)
        total_paid = 0
        total_due = 0
        total_storno = 0
        for purchase in purchases:
            popupWidgetTreeView.insert("", "end", text=purchase[0], values=("%.2f€" % purchase[1], purchase[2], "%.2f€" % (purchase[1]*purchase[2]), "B" if purchase[3] else "S" if purchase[4] else "", datetime.strptime(purchase[5], "%Y-%m-%d %H:%M:%S").strftime("%a, %H:%M")))
            total_due += 0 if (purchase[3] or purchase[4]) else (purchase[1]*purchase[2])
            total_paid += (purchase[1]*purchase[2]) if purchase[3] else 0
            total_storno += (purchase[1]*purchase[2]) if purchase[4] else 0
        total = total_due+total_paid+total_storno
        popupSVTotalSum.set("%.2f €" % total)
        popupSVTotalPaid.set("%.2f €" % total_paid)
        popupSVTotalStorno.set("%.2f €" % total_storno)
        popupSVTotalDue.set("%.2f €" % total_due)
        # configure popup window
        popupRoot.title("Summe")
        # popupRoot.overrideredirect(1)
        popupRoot.wm_attributes('-type', 'splash')
        popupRoot.attributes("-topmost", True)  # Always keep window on top of others
        popupRoot.focus_set()
        popupRoot.grab_set()  # make this the only accessible window
        popupRoot.geometry("%dx%d+%d+%d" % (800, 700, root.winfo_screenwidth() / 2 - 400, root.winfo_screenheight() / 2 - 350))
        # make parent window wait
        parent.wait_window(popupRoot)

# ---------------------------------------------- #
# ------------- Order Button Actions ----------- #
# ---------------------------------------------- #


def orderConfirm():
    global selectedItems
    player_id = getSelectedPlayerID()
    if player_id:
        if selectedItems:
            for item in selectedItems:
                insert_order = "INSERT INTO purchases (player_id, item_name, price, item_quantity, is_payed) VALUES (?, ?, ?, ?, ?)"
                data = (player_id, item[0], item[1], selectedItems[item], 0)
                runQuery(insert_order, data)
            set_payed = "UPDATE players SET is_payed=0 WHERE id = ?"
            runQuery(set_payed, (player_id,))
            selectedItems = {}
            selectedTeam.set("")        # Unselect Team
            playerDisplay("")          # Show empty Player List
            orderDisplay()
            popupNotification(root, "Buchung durchgeführt", 1500, "green")
        else:
            popupNotification(root, "Bitte Artikel auswählen", 1500, "yellow")


def orderDelete():
    global selectedItems
    selectedItems = collections.OrderedDict()
    orderDisplay()


def orderDisplay():
    orders = widgets.totalTreeViewItems.get_children()
    if orders != '()':
        for order in orders:
            widgets.totalTreeViewItems.delete(order)
    for item in selectedItems:
        widgets.totalTreeViewItems.insert("", "end", text=item[0], values=("%.2f€" % item[1], str(selectedItems[item]), "%.2f€" % (item[1]*selectedItems[item])), tags=item)
    orderUpdateTotal()


def orderUpdateTotal():
    global totalSV
    total = 0
    for item in selectedItems:
        total += item[1]*selectedItems[item]
    totalSV.set("Summe:\n%.2f €" % total)

# ---------------------------------------------- #
# ------------- Special Button Actions --------- #
# ---------------------------------------------- #


def specialRegisterClose():
    A = popupQuestionYESNO(root, "Kasse wirklich beenden?", "Beenden?", "yellow")
    if A:
        root.destroy()


def specialOrderStorno(parent):
    playerID = getSelectedPlayerID()
    if playerID:
        def stornoSelection():
            if popupWidgetTreeView.selection():
                for item in popupWidgetTreeView.selection():
                    update_storno = "UPDATE purchases SET is_storno = 1 WHERE id = ?"
                    runQuery(update_storno, (popupWidgetTreeView.item(item).get("tags")[0],))

                set_payed = "UPDATE players SET is_payed = 0 WHERE id = ?"
                runQuery(set_payed, (playerID,))
                playerDisplay(getSelectedTeam())
                popupRoot.destroy()
                popupNotification(popupRoot, "Auswahl storniert", 1500, "green")
            else:
                popupNotification(popupRoot, "Bitte eine Auswahl treffen", 1500, "yellow")

        # create window
        popupRoot = tk.Toplevel(bg="#C3C3C3")
        # create frame for treeView and ScrollBar
        popupWidgetTreeViewFrame = tk.Frame(popupRoot, bg="green")
        # create treeview
        popupWidgetTreeView = ttk.Treeview(popupWidgetTreeViewFrame, height=1)
        popupWidgetTreeView["columns"] = ("1", "2", "3", "4", "5")
        # rename treeview headings
        popupWidgetTreeView.heading("#0", text="Bestellung")
        popupWidgetTreeView.heading("1", text="Preis", anchor="center")
        popupWidgetTreeView.heading("2", text="Anzahl", anchor="center")
        popupWidgetTreeView.heading("3", text="Gesamt", anchor="center")
        popupWidgetTreeView.heading("4", text="Info", anchor="center")
        popupWidgetTreeView.heading("5", text="Zeit", anchor="center")
        # configure treeview columns
        popupWidgetTreeView.column('#0', width=100, stretch=True, anchor="w")
        popupWidgetTreeView.column('1', width=20, stretch=True, anchor="center")
        popupWidgetTreeView.column('2', width=10, stretch=True, anchor="center")
        popupWidgetTreeView.column('3', width=20, stretch=True, anchor="center")
        popupWidgetTreeView.column('4', width=10, stretch=True, anchor="center")
        popupWidgetTreeView.column('5', width=10, stretch=True, anchor="center")
        # scrollbar for tree view
        popupWidgetTreeViewVSB = tk.Scrollbar(popupWidgetTreeViewFrame, orient="vertical", command=popupWidgetTreeView.yview, width=35)
        popupWidgetTreeView.configure(yscrollcommand=popupWidgetTreeViewVSB.set)
        # create widgets
        popupSVTotalSum = tk.StringVar()
        popupWidgetDescTotal = tk.Label(popupRoot, text="Summe der Einkäufe:")
        popupWidgetLabelTotal = tk.Label(popupRoot, textvariable=popupSVTotalSum)
        popupWidgetLabelExplanation = tk.Label(popupRoot, text="Für eine Mehrfachauswahl >STRG< gedrückt halten")
        popupWidgetButtonAbort = tk.Button(popupRoot, text="Abbrechen", command=lambda: popupRoot.destroy(), width=1)
        popupWidgetButtonStorno = tk.Button(popupRoot, text="Stornieren", command=lambda: stornoSelection(), width=1)
        # configure widgets
        popupPixel = tk.PhotoImage(width=1, height=1)
        popupWidgetDescTotal.configure(image=popupPixel, compound="center", anchor="e", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetLabelTotal.configure(image=popupPixel, compound="center", anchor="w", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetLabelExplanation.configure(image=popupPixel, compound="center", anchor="center", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetButtonAbort.configure(image=popupPixel, compound="center", font=(None, 15), width=1, height=1, highlightbackground="#C3C3C3")
        popupWidgetButtonStorno.configure(image=popupPixel, compound="center", font=(None, 15), width=1, height=1, highlightbackground="#C3C3C3")
        # place widgets on grid
        popupWidgetTreeViewFrame.grid(column=0, row=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetDescTotal.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetLabelTotal.grid(column=1, row=1, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetLabelExplanation.grid(column=0, row=2, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetButtonAbort.grid(column=0, row=3, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetButtonStorno.grid(column=1, row=3, sticky=tk.NSEW, padx=10, pady=10)
        # use pack for treeview and vsb
        popupWidgetTreeView.pack(fill="both", side="left", expand=tk.TRUE)
        popupWidgetTreeViewVSB.pack(fill="both", side="right")
        # configure grid
        popupRoot.rowconfigure(0, weight=32)
        popupRoot.rowconfigure(1, weight=2)
        popupRoot.rowconfigure(2, weight=2)
        popupRoot.rowconfigure(3, weight=2)
        popupRoot.columnconfigure(0, weight=1)
        popupRoot.columnconfigure(1, weight=1)
        # sum up purchases
        select_purchases = "SELECT item_name, price, item_quantity, is_payed, id, datetime(purchase_time,'localtime') FROM purchases WHERE player_id = ? AND is_storno = 0 AND is_payed = 0"
        purchases = runQuery(select_purchases, (playerID,), receive=tk.TRUE)
        total = 0
        # create an entry in the treeview for every bought item
        for purchase in purchases:
            popupWidgetTreeView.insert("", "end", text=purchase[0], values=(
                "%.2f€" % purchase[1], purchase[2], "%.2f€" % (purchase[1] * purchase[2]), "x" if purchase[3] else "",
                datetime.strptime(purchase[5], "%Y-%m-%d %H:%M:%S").strftime("%a, %H:%M")), tags=purchase[4])
            total += (purchase[1] * purchase[2])
        popupSVTotalSum.set(str(total) + " €")
        # configure popup window
        popupRoot.title("Stornieren")
        # popupRoot.overrideredirect(1)
        popupRoot.wm_attributes('-type', 'splash')
        popupRoot.attributes("-topmost", True)  # Always keep window on top of others
        popupRoot.focus_set()
        popupRoot.grab_set()  # make this the only accessible window
        popupRoot.geometry("%dx%d+%d+%d" % (800, 700, root.winfo_screenwidth() / 2 - 400, root.winfo_screenheight() / 2 - 350))
        # make parent window wait
        parent.wait_window(popupRoot)


def specialPayPlayerAdd(parent):
    def callback(event=None):
        popupRoot.destroy()

    if True:
        # create popup window
        popupRoot = tk.Toplevel(bg="#C3C3C3")
        # create widgets
        popupWidgetTreeViewFrameTeams = tk.Frame(popupRoot, bg="green")
        popupWidgetTreeViewFramePlayers = tk.Frame(popupRoot, bg="green")
        popupWidgetTreeViewTeams = ttk.Treeview(popupWidgetTreeViewFrameTeams, height=1)
        popupWidgetTreeViewPlayers = ttk.Treeview(popupWidgetTreeViewFramePlayers, height=1)
        popupWidgetTreeViewTeams.heading("#0", text="Teams")
        popupWidgetTreeViewPlayers.heading("#0", text="Players")
        popupWidgetTreeViewTeams.column('#0', width=100, stretch=True, anchor="w")
        popupWidgetTreeViewPlayers.column('#0', width=100, stretch=True, anchor="w")
        # scrollbar for tree view
        popupWidgetTreeViewTeamsVSB = tk.Scrollbar(popupWidgetTreeViewFrameTeams, orient="vertical", command=popupWidgetTreeViewTeams.yview, width=35)
        popupWidgetTreeViewTeams.configure(yscrollcommand=popupWidgetTreeViewTeamsVSB.set)
        popupWidgetTreeViewPlayersVSB = tk.Scrollbar(popupWidgetTreeViewFramePlayers, orient="vertical", command=popupWidgetTreeViewPlayers.yview, width=35)
        popupWidgetTreeViewPlayers.configure(yscrollcommand=popupWidgetTreeViewPlayersVSB.set)
        # create buttons
        popupWidgetButtonAbort = tk.Button(popupRoot, text="Abbrechen", command=lambda: popupRoot.destroy())
        popupWidgetButtonOK = tk.Button(popupRoot, text="OK", command=lambda: callback())
        # configure widgets
        popupPixel = tk.PhotoImage(width=1, height=1)
        popupWidgetButtonAbort.configure(image=popupPixel, compound="center", font=(None, 15), width=1, height=1, highlightbackground="#C3C3C3")
        popupWidgetButtonOK.configure(image=popupPixel, compound="center", font=(None, 20), width=1, height=1, highlightbackground="#C3C3C3")
        # place on grid
        popupWidgetTreeViewFrameTeams.grid( row=0, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetTreeViewFramePlayers.grid( row=1, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetButtonAbort.grid(row=2, column=0, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetButtonOK.grid(row=2, column=1, sticky=tk.NSEW, padx=10, pady=10)
        # use pack for treeview and vsb
        popupWidgetTreeViewTeams.pack(fill="both", side="left", expand=tk.TRUE)
        popupWidgetTreeViewTeamsVSB.pack(fill="both", side="right")
        popupWidgetTreeViewPlayers.pack(fill="both", side="left", expand=tk.TRUE)
        popupWidgetTreeViewPlayersVSB.pack(fill="both", side="right")
        # configure grid
        popupRoot.rowconfigure(0, weight=2)
        popupRoot.rowconfigure(1, weight=2)
        popupRoot.rowconfigure(2, weight=1)
        popupRoot.columnconfigure(0, weight=1)
        popupRoot.columnconfigure(1, weight=1)
        # configure popup window
        popupRoot.title("Weiteren Spieler abrechnen")
        # popupRoot.overrideredirect(1)
        popupRoot.wm_attributes('-type', 'splash')
        popupRoot.attributes("-topmost", True)  # Always keep window on top of others
        popupRoot.focus_set()
        popupRoot.grab_set()  # make this the only accessible window
        popupRoot.geometry("%dx%d+%d+%d" % (400, 400, root.winfo_screenwidth() / 2 - 200, root.winfo_screenheight() / 2 - 200))
        # set callback
        popupRoot.bind("<Return>", callback)
        # make parent window wait
        parent.wait_window(popupRoot)


def specialPlayerPay(parent):
    playerID = getSelectedPlayerID()
    if playerID:
        # run SQL query
        def deduction():
            pay_purchases = "UPDATE purchases SET is_payed = 1 WHERE player_id = ?"
            runQuery(pay_purchases, (playerID,))
            set_payed = "UPDATE players SET is_payed = 1 WHERE id = ?"
            runQuery(set_payed, (playerID,))
            playerDisplay(getSelectedTeam())
            popupRoot.destroy()
        # run SQL query

        def addPlayer():
            specialPayPlayerAdd(parent)

        def callbackEnterGiven(*args):
            returnMoney = float(popupSVGiven.get()) - total_due
            popupSVReturn.set("%.2f" % returnMoney )

        # create window
        popupRoot = tk.Toplevel(bg="#C3C3C3")
        # create treeview for player name list
        popupWidgetTreeViewPlayersFrame = tk.Frame(popupRoot, bg="green")
        popupWidgetTreeViewPlayers = ttk.Treeview(popupWidgetTreeViewPlayersFrame, height=1)
        popupWidgetTreeViewPlayers["columns"] = ("Summe")
        popupWidgetTreeViewPlayers.heading("#0", text="Name", anchor=tk.W)
        popupWidgetTreeViewPlayers.heading("Summe", text="Summe")
        popupWidgetTreeViewPlayers.column('#0', width=1, stretch=True)
        popupWidgetTreeViewPlayers.column('Summe', width=1, stretch=True)
        popupWidgetTreeViewPlayersVSB = tk.Scrollbar(popupWidgetTreeViewPlayersFrame, orient="vertical", command=popupWidgetTreeViewPlayers.yview, width=35)
        popupWidgetTreeViewPlayers.configure(yscrollcommand=popupWidgetTreeViewPlayersVSB.set)
        # create frame for treeView and ScrollBar
        popupWidgetTreeViewFrame = tk.Frame(popupRoot, bg="green")
        # create treeview
        popupWidgetTreeView = ttk.Treeview(popupWidgetTreeViewFrame, height=1)
        popupWidgetTreeView["columns"] = ("Spieler", "Preis", "Anzahl", "Gesamt", "Bezahlt")
        # configure treeview headings
        popupWidgetTreeView.heading("#0", text="Bestellung")
        popupWidgetTreeView.heading("Spieler", text="Spieler", anchor=tk.W)
        popupWidgetTreeView.heading("Preis", text="Preis", anchor=tk.W)
        popupWidgetTreeView.heading("Anzahl", text="Anzahl", anchor=tk.W)
        popupWidgetTreeView.heading("Gesamt", text="Gesamt")
        popupWidgetTreeView.heading("Bezahlt", text="Bezahlt")
        # configure treeview columns
        popupWidgetTreeView.column('#0', width=100, stretch=True)
        popupWidgetTreeView.column('Spieler', width=20, stretch=True)
        popupWidgetTreeView.column('Preis', width=20, stretch=True)
        popupWidgetTreeView.column('Anzahl', width=10, stretch=True)
        popupWidgetTreeView.column('Gesamt', width=20, stretch=True)
        popupWidgetTreeView.column('Bezahlt', width=10, stretch=True)
        # scrollbar for tree view
        popupWidgetTreeViewVSB = tk.Scrollbar(popupWidgetTreeViewFrame, orient="vertical", command=popupWidgetTreeView.yview, width=35)
        popupWidgetTreeView.configure(yscrollcommand=popupWidgetTreeViewVSB.set)
        # create string variables
        popupSVTotalSum = tk.StringVar()
        popupSVTotalPaid = tk.StringVar()
        popupSVTotalStorno = tk.StringVar()
        popupSVTotalDue = tk.StringVar()
        popupSVGiven = tk.StringVar()
        popupSVGiven.trace_add("write", callbackEnterGiven)
        popupSVReturn = tk.StringVar()
        #
        popupWidgetButtonAddPlayer = tk.Button(popupRoot, text="Spieler hinzufügen", command=lambda: addPlayer())
        # create widgets
        popupWidgetDescTotal = tk.Label(popupRoot, text="Summe:")
        popupWidgetDescPaid = tk.Label(popupRoot, text="Bisher bezahlt:")
        popupWidgetDescStorno = tk.Label(popupRoot, text="Storniert:")
        popupWidgetDescDue = tk.Label(popupRoot, text="Übrig:")
        popupWidgetLabelTotal = tk.Label(popupRoot, textvariable=popupSVTotalSum)
        popupWidgetLabelPaid = tk.Label(popupRoot, textvariable=popupSVTotalPaid)
        popupWidgetLabelStorno = tk.Label(popupRoot, textvariable=popupSVTotalStorno)
        popupWidgetLabelDue = tk.Label(popupRoot, textvariable=popupSVTotalDue)
        popupWidgetLabelInfo = tk.Label(popupRoot, text="Notiz:")
        popupWidgetTextInfo = tk.Text(popupRoot)
        #
        popupWidgetDescGiven = tk.Label(popupRoot, text="Gegeben:")
        popupWidgetDescReturn = tk.Label(popupRoot, text="Zurück:")
        popupWidgetLabelGiven = tk.Entry(popupRoot, textvariable=popupSVGiven)
        popupWidgetLabelReturn = tk.Label(popupRoot, textvariable=popupSVReturn)
        #
        popupWidgetButtonAbort = tk.Button(popupRoot, text="Abbrechen", command=lambda: popupRoot.destroy())
        popupWidgetButtonPay = tk.Button(popupRoot, text="Bezahlen", command=lambda: deduction())
        # configure widgets
        popupPixel = tk.PhotoImage(width=1, height=1)
        popupWidgetDescTotal.configure(image=popupPixel, compound="center", anchor="e", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetDescPaid.configure(image=popupPixel, compound="center", anchor="e", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetDescStorno.configure(image=popupPixel, compound="center", anchor="e", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetDescDue.configure(image=popupPixel, compound="center", anchor="e", font=(None, 15, "bold"), width=1, height=1, bg="#C3C3C3")
        popupWidgetLabelTotal.configure(image=popupPixel, compound="center", anchor="w", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetLabelPaid.configure(image=popupPixel, compound="center", anchor="w", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetLabelStorno.configure(image=popupPixel, compound="center", anchor="w", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetLabelDue.configure(image=popupPixel, compound="center", anchor="w", font=(None, 15, "bold"), width=1, height=1, bg="#C3C3C3")
        popupWidgetLabelInfo.configure(image=popupPixel, compound="center", anchor="w", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetTextInfo.configure(height=1, width=1)
        popupWidgetButtonAddPlayer.configure(image=popupPixel, compound="center", font=(None, 15), width=1, height=1, highlightbackground="#C3C3C3")
        popupWidgetButtonAbort.configure(image=popupPixel, compound="center", font=(None, 15), width=1, height=1, highlightbackground="#C3C3C3")
        popupWidgetButtonPay.configure(image=popupPixel, compound="center", font=(None, 15), width=1, height=1, highlightbackground="#C3C3C3")
        #
        popupWidgetDescGiven.configure(image=popupPixel, compound="center", anchor="e", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetDescReturn.configure(image=popupPixel, compound="center", anchor="e", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetLabelGiven.configure(justify="center", font=(None, 15, "bold"))
        popupWidgetLabelReturn.configure(justify="center", font=(None, 15, "bold"))
        # place widgets on grid
        popupWidgetTreeViewPlayersFrame.grid(column=0, row=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetButtonAddPlayer.grid(column=2, row=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)

        popupWidgetTreeViewFrame.grid(column=0, row=1, columnspan=4, sticky=tk.NSEW, padx=10, pady=10)

        popupWidgetDescTotal.grid(column=0, row=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetDescPaid.grid(column=0, row=3, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetDescStorno.grid(column=0, row=4, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetDescDue.grid(column=0, row=5, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetLabelTotal.grid(column=1, row=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetLabelPaid.grid(column=1, row=3, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetLabelStorno.grid(column=1, row=4, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetLabelDue.grid(column=1, row=5, sticky=tk.NSEW, padx=10, pady=10)

        popupWidgetLabelInfo.grid(column=2, row=2, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetTextInfo.grid(column=2, row=3, columnspan=2, rowspan=3, sticky=tk.NSEW, padx=10, pady=10)
        #
        popupWidgetDescGiven.grid(column=0, row=6, columnspan=1, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetDescReturn.grid(column=0, row=7, columnspan=1, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetLabelGiven.grid(column=1, row=6, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetLabelReturn.grid(column=1, row=7, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        #
        popupWidgetButtonAbort.grid(column=0, row=8, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetButtonPay.grid(column=2, row=8, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        # use pack for treeview and vsb
        popupWidgetTreeViewPlayers.pack(fill="both", side="left", expand=tk.TRUE)
        popupWidgetTreeViewPlayersVSB.pack(fill="both", side="right")
        popupWidgetTreeView.pack(fill="both", side="left", expand=tk.TRUE)
        popupWidgetTreeViewVSB.pack(fill="both", side="right")
        # configure grid
        popupRoot.columnconfigure(0, weight=1)
        popupRoot.columnconfigure(1, weight=1)
        popupRoot.columnconfigure(2, weight=1)
        popupRoot.columnconfigure(3, weight=1)
        popupRoot.rowconfigure(0, weight=2)
        popupRoot.rowconfigure(1, weight=28)
        popupRoot.rowconfigure(2, weight=2)
        popupRoot.rowconfigure(3, weight=2)
        popupRoot.rowconfigure(4, weight=2)
        popupRoot.rowconfigure(5, weight=2)
        popupRoot.rowconfigure(6, weight=2)
        popupRoot.rowconfigure(7, weight=2)
        popupRoot.rowconfigure(8, weight=4)
        # sum up purchases
        select_purchases = "SELECT item_name, price, SUM(item_quantity), is_payed, is_storno FROM purchases WHERE player_id = ? GROUP BY item_name, price, is_payed, is_storno"
        purchases = runQuery(select_purchases, (playerID,), receive=tk.TRUE)
        total_paid = 0
        total_due = 0
        total_storno = 0
        for purchase in purchases:
            popupWidgetTreeView.insert("", "end", text=purchase[0], values=("%.2f€" % purchase[1], purchase[2], "%.2f€" % (purchase[1]*purchase[2]), "B" if purchase[3] else "S" if purchase[4] else ""))
            total_due += 0 if (purchase[3] or purchase[4]) else (purchase[1]*purchase[2])
            total_paid += (purchase[1]*purchase[2]) if purchase[3] else 0
            total_storno += (purchase[1]*purchase[2]) if purchase[4] else 0
        total = total_due+total_paid+total_storno
        popupSVTotalSum.set("%.2f €" % total)
        popupSVTotalPaid.set("%.2f €" % total_paid)
        popupSVTotalStorno.set("%.2f €" % total_storno)
        popupSVTotalDue.set("%.2f €" % total_due)
        # run SQL query

        def deduction():
            pay_purchases = "UPDATE purchases SET is_payed = 1 WHERE player_id = ? AND is_storno = 0"
            runQuery(pay_purchases, (playerID,))
            set_payed = "UPDATE players SET is_payed = 1 WHERE id = ?"
            runQuery(set_payed, (playerID,))
            playerDisplay(getSelectedTeam())
            popupRoot.destroy()
        # configure popup window
        popupRoot.title("Spieler Abrechnen")
        # popupRoot.overrideredirect(1)
        popupRoot.wm_attributes('-type', 'splash')
        popupRoot.attributes("-topmost", True)  # Always keep window on top of others
        popupRoot.focus_set()
        popupRoot.grab_set()  # make this the only accessible window
        windowHeight = 700
        windwowWidth = 800
        popupRoot.geometry("%dx%d+%d+%d" % (windwowWidth, windowHeight, (root.winfo_screenwidth() - windwowWidth) / 2, (root.winfo_screenheight() - windowHeight) / 2))
        # make parent window wait
        parent.wait_window(popupRoot)


def specialPlayerAddNote(parent):
    playerID = getSelectedPlayerID()
    if playerID:
        def callback():
            return

        # create popup window
        popupRoot = tk.Toplevel(parent, bg="#C3C3C3")
        # create widgets
        popupWidgetLabel = tk.Label(popupRoot, text="Notiz hinzufügen / bearbeiten")
        popupWidgetText = tk.Text(popupRoot)
        popupWidgetButtonAbort = tk.Button(popupRoot, text="Abbrechen", command=lambda: popupRoot.destroy())
        popupWidgetButtonSave = tk.Button(popupRoot, text="OK", command=lambda: callback())
        # configure widgets
        popupPixel = tk.PhotoImage(width=1, height=1)
        popupWidgetLabel.configure(image=popupPixel, compound="center", font=(None, 15), width=1, height=1, bg="#C3C3C3")
        popupWidgetText.configure(font=(None, 15), width=1, height=1)
        popupWidgetButtonAbort.configure(image=popupPixel, compound="center", font=(None, 15), width=1, height=1, highlightbackground="#C3C3C3")
        popupWidgetButtonSave.configure(image=popupPixel, compound="center", font=(None, 20), width=1, height=1, highlightbackground="#C3C3C3")
        # place on grid
        popupWidgetLabel.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetText.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetButtonAbort.grid(row=2, column=0, sticky=tk.NSEW, padx=10, pady=10)
        popupWidgetButtonSave.grid(row=2, column=1, sticky=tk.NSEW, padx=10, pady=10)
        # configure grid
        popupRoot.rowconfigure(0, weight=1)
        popupRoot.rowconfigure(1, weight=10)
        popupRoot.rowconfigure(2, weight=2)
        popupRoot.columnconfigure(0, weight=1)
        popupRoot.columnconfigure(1, weight=1)
        # configure popup window
        popupRoot.title("Spieler hinzufügen")
        # popupRoot.overrideredirect(1)
        popupRoot.wm_attributes('-type', 'splash')
        popupRoot.attributes("-topmost", True)  # Always keep window on top of others
        popupRoot.focus_set()
        popupRoot.grab_set()  # make this the only accessible window
        popupRoot.geometry("%dx%d+%d+%d" % (400, 400, root.winfo_screenwidth() / 2 - 200, root.winfo_screenheight() / 2 - 200))
        # set focus and callback
        popupWidgetText.focus()
        popupRoot.bind("<Return>", callback)
        # make parent window wait
        parent.wait_window(popupRoot)


# -------------------------------------------------------------------------------------------- #
# ----------------------------------- Create Layout ------------------------------------------ #
# -------------------------------------------------------------------------------------------- #

pixel = tk.PhotoImage(width=1, height=1)

style = ttk.Style()
style.configure("Treeview", font=("Verdana", 15), rowheight=45)
style.configure("Treeview.Heading", font=("Verdana", 10))

# ---------------------------------------------- #
# ------------- Create Main Frames ------------- #
# ---------------------------------------------- #
# these are the statusbar and the main application area

frames.main = tk.Frame(root, bg="red")
frames.statusbar = tk.Frame(root, bg="#DBDF31")

frames.main.grid(row=0, column=0, sticky=tk.NSEW)
frames.statusbar.grid(row=1, column=0, sticky=tk.NSEW)

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0, minsize=30)
root.columnconfigure(0, weight=1)

# ---------------------------------------------- #
# ------------- Left and Right main frames ----- #
# ---------------------------------------------- #
# here the main application area is split equally into the left and right columns
# this is probably not needed -> I just have to set the grid correctly and get rid of the 'mainLeft' and 'mainRight' frames

frames.mainLeft = tk.Frame(frames.main, bg="pink")
frames.mainRight = tk.Frame(frames.main, bg="orange")

frames.mainLeft.grid(row=0, column=0, sticky=tk.NSEW)
frames.mainRight.grid(row=0, column=1, sticky=tk.NSEW)

frames.main.columnconfigure(0, weight=1)
frames.main.columnconfigure(1, weight=1)
frames.main.rowconfigure(0, weight=1)

# ---------------------------------------------- #
# ------------- Create Subframes --------------- #
# ---------------------------------------------- #
# now four frames are created for the teams, players, items, and the total view
# teams and players go into the 'left' area and are set next to each other
# items and total are set into the 'right' area and are above one another

frames.teams = tk.Frame(frames.mainLeft, bg="#C3C3C3")
frames.players = tk.Frame(frames.mainLeft, bg="#FC5252")
frames.items = tk.Frame(frames.mainRight, bg="#5AAE4A")
frames.total = tk.Frame(frames.mainRight, bg="#4A98AE")

frames.teams.grid(row=0, column=0, sticky=tk.NSEW)
frames.players.grid(row=0, column=1, sticky=tk.NSEW)

frames.items.grid(row=0, column=0, sticky=tk.NSEW)
frames.total.grid(row=1, column=0, sticky=tk.NSEW)

frames.mainLeft.columnconfigure(0, weight=8)
frames.mainLeft.columnconfigure(1, weight=5)
frames.mainLeft.rowconfigure(0, weight=1)

frames.mainRight.rowconfigure(0, weight=1)
frames.mainRight.rowconfigure(1, weight=1)
frames.mainRight.columnconfigure(0, weight=1)

frames.teams.grid_propagate(False)
frames.players.grid_propagate(False)
frames.items.grid_propagate(False)
frames.total.grid_propagate(False)

# ---------------------------------------------- #
# ------------- fill team frame ---------------- #
# ---------------------------------------------- #

widgets.teambuttons = {}
assets.teamimageOn = {}
assets.teamimageOff = {}
assets.teamimageResizeOn = {}
assets.teamimageResizeOff = {}

f = open("teams.txt", "r")
assets.teamList = f.readlines()
f.close()
assets.teamList = list(map(str.strip, assets.teamList))

# load team images and store
for i in range(len(assets.teamList)):
    assets.teamimageOn[i] = Image.open("Logo_" + assets.teamList[i] + "_On.gif")
    assets.teamimageOff[i] = Image.open("Logo_" + assets.teamList[i] + "_Off.gif")

# create buttons
for i in range(len(assets.teamList)):
    widgets.teambuttons[i] = tk.Radiobutton(frames.teams, command=partial(onSelectTeam, assets.teamList[i]), value=assets.teamList[i], variable=selectedTeam)
    # widgets.teambuttons[i].configure(text=assets.teamList[i], indicatoron=tk.FALSE, bg="#C3C3C3", height=1, width=1, image=pixel, highlightbackground="#C3C3C2", background="#C3C3C3"
    # widgets.teambuttons[i].grid(row=i // 3, column=i % 3, sticky=tk.NSEW, padx=0, pady=0)
    nrows = 1
    ncols = 1
    widgets.teambuttons[i].configure(text=assets.teamList[i], indicatoron=tk.FALSE, font=("Verdana", 18, "bold"), height=1, width=1, compound="center", borderwidth=0, bg="blue", fg="white")
    widgets.teambuttons[i].grid(row=i // nrows, column=i % ncols, sticky=tk.NSEW, padx=0, pady=0)

# configure team frame so that contents scale
for col_num in range(frames.teams.grid_size()[0]):
    frames.teams.columnconfigure(col_num, weight=1)
for row_num in range(frames.teams.grid_size()[1]):
    frames.teams.rowconfigure(row_num, weight=1)

def ResizeTeamImages():
    # print("resize team image called")
    root.update_idletasks()
    frames.teams.update()
    for ii in range(len(assets.teamList)):
        teamimagesize = min(widgets.teambuttons[ii].winfo_height(), widgets.teambuttons[ii].winfo_width())
        teamimagesize = widgets.teambuttons[ii].winfo_width()
        # resize images
        assets.teamimageResizeOn[ii] = ImageTk.PhotoImage(image=assets.teamimageOn[ii].resize((teamimagesize, teamimagesize), resample=Image.Resampling.LANCZOS))
        assets.teamimageResizeOff[ii] = ImageTk.PhotoImage(image=assets.teamimageOff[ii].resize((teamimagesize, teamimagesize), resample=Image.Resampling.LANCZOS))
        # assign images
        widgets.teambuttons[ii].config(image=assets.teamimageResizeOn[ii])
        widgets.teambuttons[ii].config(selectimage=assets.teamimageResizeOff[ii])


ResizeTeamImages()

# frames.teams.bind("<Configure>", ResizeTeamImages())

# ---------------------------------------------- #
# ------------- fill players frame ------------- #
# ---------------------------------------------- #

frames.playerTreeViewFrame = tk.Frame(frames.players, bg="green")

widgets.playerTreeView = ttk.Treeview(frames.playerTreeViewFrame, height=1)
widgets.playerTreeView["columns"] = ("one")
widgets.playerTreeView.heading("#0",  text="Spieler", anchor="w")
widgets.playerTreeView.heading("one", text="B", anchor="center")
widgets.playerTreeView.column("#0", width=100, stretch=True, anchor="w")
widgets.playerTreeView.column("one", width=20, stretch=True, anchor="center")

widgets.playerTreeViewVSB = tk.Scrollbar(frames.playerTreeViewFrame, orient="vertical", command=widgets.playerTreeView.yview, width=35)
widgets.playerTreeView.configure(yscrollcommand=widgets.playerTreeViewVSB.set)

widgets.playerButtonAdd = tk.Button(frames.players, text="Spieler hinzufügen", command=lambda: playerAdd(root))
widgets.playerButtonRename = tk.Button(frames.players, text="Spieler umbenennen", command=lambda: playerRename(root))
widgets.playerButtonShowSum = tk.Button(frames.players, text="Summe anzeigen", command=lambda: playerShowSum(root))

widgets.playerButtonAdd.configure(image=pixel, font=("Verdana", 15), height=1, compound="center", highlightbackground="#973131")
widgets.playerButtonRename.configure(image=pixel, font=("Verdana", 15), height=1, compound="center", highlightbackground="#973131")
widgets.playerButtonShowSum.configure(image=pixel, font=("Verdana", 15), height=1, compound="center", highlightbackground="#973131")

frames.playerTreeViewFrame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
widgets.playerButtonAdd.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
widgets.playerButtonRename.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=5)
widgets.playerButtonShowSum.grid(row=3, column=0, sticky=tk.NSEW, padx=5, pady=5)

widgets.playerTreeView.pack(fill="both", side="left", expand=tk.TRUE)
widgets.playerTreeViewVSB.pack(fill="both", side="right")

frames.players.rowconfigure(0, weight=15)
frames.players.rowconfigure(1, weight=1)
frames.players.rowconfigure(2, weight=1)
frames.players.rowconfigure(3, weight=1)
frames.players.columnconfigure(0, weight=1)


def ResizePlayerTreeViewColumn():
    # print("resize team image called")
    root.update_idletasks()
    frames.players.update()
    treeviewWidth = widgets.playerTreeView.winfo_width()
    widgets.playerTreeView.column("#0", width=int(treeviewWidth/10*9), stretch=True, anchor="e")
    widgets.playerTreeView.column("one", width=int(treeviewWidth/10*1), stretch=True, anchor="center")


ResizePlayerTreeViewColumn()

# ---------------------------------------------- #
# -------------fill item frame ----------------- #
# ---------------------------------------------- #

items = SimpleNamespace()
items.name = []
items.price = []
items.category = []

frames.itemcategories = {}
widgets.itembutton = {}

# read food file
f = open("food.txt", "r")
assets.foodList = f.readlines()
f.close()

settings.itemsPerRow = 4

for i in range(len(assets.foodList)):
    [name, price, category] = assets.foodList[i].strip().split(";")
    items.name.append(name)
    items.price.append(price)
    items.category.append(int(category))

# create category containers
for i in range(len(set(items.category))):
    # create frames and put onto grid
    frames.itemcategories[i] = tk.Frame(frames.items, bg="#71C968")
    frames.itemcategories[i].grid(column=0, row=i, sticky=tk.NSEW, padx=5, pady=5)
    # calc needed weight for each frame
    rowweight = math.ceil(items.category.count(sorted(set(items.category))[i]) / settings.itemsPerRow)
    # configure with correct weight
    frames.items.rowconfigure(i, weight=rowweight)
    frames.items.columnconfigure(0, weight=1)

# create item buttons
for i in range(len(items.name)):
    widgets.itembutton[i] = tk.Button(frames.itemcategories[items.category[i]], command=partial(onClickItem, items.name[i], float(items.price[i])))
    # buttontext = items.name[i] + " " + str(items.price[i]) + "€"
    buttontext = items.name[i] + "\n" + str(items.price[i]) + "€"
    widgets.itembutton[i].config(image=pixel, compound="center", text=buttontext, font=("Verdana", 12), width=1, highlightbackground="#44793E")
    # figure out position of button widget in current category frame
    currentint = 0
    for j in range(i):
        if items.category[j] == items.category[i]:
            currentint = currentint + 1
    # place widget in category frame
    widgets.itembutton[i].grid(row=(currentint)//settings.itemsPerRow, column=(currentint) % settings.itemsPerRow, sticky=tk.NSEW, pady=5, padx=5)

for i in range(len(frames.itemcategories)):
    # for j in range(frames.itemcategories[i].grid_size()[0]):
    # print("container "+str(i))
    for j in range(settings.itemsPerRow):
        frames.itemcategories[i].columnconfigure(j, weight=1)
        # print("column "+str(j))
    for j in range(frames.itemcategories[i].grid_size()[1]):
        # print("row "+str(j))
        frames.itemcategories[i].rowconfigure(j, weight=1)

# ---------------------------------------------- #
# -------------fill total frame ---------------- #
# ---------------------------------------------- #

frames.totalTreeViewFrame = tk.Frame(frames.total, bg="green")

widgets.totalTreeViewItems = ttk.Treeview(frames.totalTreeViewFrame)
widgets.totalTreeViewItems["columns"] = ("Preis", "Anzahl", "Gesamt")
widgets.totalTreeViewItems.heading("#0",  text="Bestellung", anchor="w")
widgets.totalTreeViewItems.heading("Preis", text="Preis", anchor="center")
widgets.totalTreeViewItems.heading("Anzahl", text="#", anchor="center")
widgets.totalTreeViewItems.heading("Gesamt", text="Gesamt", anchor="center")
widgets.totalTreeViewItems.column('#0', width=1, stretch=True, anchor="w")
widgets.totalTreeViewItems.column('Preis', width=1, stretch=True, anchor="center")
widgets.totalTreeViewItems.column('Anzahl', width=1, stretch=True, anchor="center")
widgets.totalTreeViewItems.column('Gesamt', width=1, stretch=True, anchor="center")
widgets.totalTreeViewItems.bind('<<TreeviewSelect>>', onSelectOrder)

widgets.totalTreeViewItemsVSB = tk.Scrollbar(frames.totalTreeViewFrame,orient="vertical",command=widgets.totalTreeViewItems.yview, width=35)
widgets.totalTreeViewItems.configure(yscrollcommand=widgets.totalTreeViewItemsVSB.set)

widgets.totalLabelSum = tk.Label(frames.total, textvariable=totalSV)
widgets.totalButtonClear = tk.Button(frames.total, text="Auswahl\nlöschen", command=orderDelete, highlightbackground="#307F95")
widgets.totalButtonConfirm = tk.Button(frames.total, text="Buchung\nbestätigen", command=orderConfirm, highlightbackground="#307F95")

widgets.totalLabelSum.configure(image=pixel, font=("Verdana", 15), relief="sunken", height=1, compound="center", width=1)
widgets.totalButtonClear.configure(image=pixel, compound="center", font=("Verdana", 10), height=1, width=1)
widgets.totalButtonConfirm.configure(image=pixel, compound="center", font=("Verdana", 15), height=1, width=1)

frames.totalTreeViewFrame.grid(column=0, row=0, rowspan=3, sticky=tk.NSEW, padx=5, pady=5)
widgets.totalLabelSum.grid(column=1, row=0, sticky=tk.NSEW, padx=5, pady=5)
widgets.totalButtonClear.grid(column=1, row=1, sticky=tk.NSEW, padx=5, pady=5)
widgets.totalButtonConfirm.grid(column=1, row=2, sticky=tk.NSEW, padx=5, pady=5)

widgets.totalTreeViewItems.pack(fill="both", side="left", expand=tk.TRUE)
widgets.totalTreeViewItemsVSB.pack(fill="both", side="right")

frames.total.rowconfigure(0, weight=3)
frames.total.rowconfigure(1, weight=2)
frames.total.rowconfigure(2, weight=5)
frames.total.columnconfigure(0, weight=4)
frames.total.columnconfigure(1, weight=1)


def ResizeTotalTreeViewColumn():
    root.update_idletasks()
    frames.total.update()
    treeviewWidth = widgets.totalTreeViewItems.winfo_width()
    widgets.totalTreeViewItems.column('#0', width=int(treeviewWidth/11 * 4))
    widgets.totalTreeViewItems.column('Preis', width=int(treeviewWidth/11 * 3))
    widgets.totalTreeViewItems.column('Anzahl', width=int(treeviewWidth/11 * 1))
    widgets.totalTreeViewItems.column('Gesamt', width=int(treeviewWidth/11 * 3))


ResizeTotalTreeViewColumn()

# ---------------------------------------------- #
# -------------fill status bar ----------------- #
# ---------------------------------------------- #

timeSV = tk.StringVar()

widgets.statusbarButtonExit = tk.Button(frames.statusbar, text="Kasse Beenden", command=specialRegisterClose)
widgets.statusbarButtonStorno = tk.Button(frames.statusbar, text="Buchung stornieren", command=lambda: specialOrderStorno(root))
widgets.statusbarButtonPay = tk.Button(frames.statusbar, text="Spieler abrechnen", command=lambda: specialPlayerPay(root))
widgets.statusbarButtonAddNote = tk.Button(frames.statusbar, text="Notiz hinzufügen", command=lambda: specialPlayerAddNote(root))
widgets.statusbarButtonExportDB = tk.Button(frames.statusbar, text="Datenbank exportieren", command=lambda: sqlExportDB())
widgets.statusbarLabelTime = tk.Label(frames.statusbar, textvariable=timeSV)

widgets.statusbarButtonExit.configure(image=pixel, compound="center", font=("Verdana", 10), height=1, width=1, highlightbackground="#DBDF31")
widgets.statusbarButtonStorno.configure(image=pixel, compound="center", font=("Verdana", 10), height=1, width=1, highlightbackground="#DBDF31")
widgets.statusbarButtonPay.configure(image=pixel, compound="center", font=("Verdana", 10), height=1, width=1, highlightbackground="#DBDF31")
widgets.statusbarButtonAddNote.configure(image=pixel, compound="center", font=("Verdana", 10), height=1, width=1, highlightbackground="#DBDF31")
widgets.statusbarButtonExportDB.configure(image=pixel, compound="center", font=("Verdana", 10), height=1, width=1, highlightbackground="#DBDF31")
widgets.statusbarLabelTime.configure(image=pixel, compound="right", anchor="e", font=("Verdana", 15), height=1, width=1, highlightbackground="#DBDF31", background="#DBDF31")

widgets.statusbarButtonExit.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=2)
widgets.statusbarButtonStorno.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=2)
widgets.statusbarButtonPay.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=2)
widgets.statusbarButtonAddNote.grid(row=0, column=3, sticky=tk.NSEW, padx=5, pady=2)
widgets.statusbarButtonExportDB.grid(row=0, column=4, sticky=tk.NSEW, padx=5, pady=2)
widgets.statusbarLabelTime.grid(row=0, column=5, sticky=tk.NSEW, padx=10, pady=2)

frames.statusbar.columnconfigure(0, weight=1)
frames.statusbar.columnconfigure(1, weight=1)
frames.statusbar.columnconfigure(2, weight=1)
frames.statusbar.columnconfigure(3, weight=1)
frames.statusbar.columnconfigure(4, weight=1)
frames.statusbar.columnconfigure(5, weight=1)
frames.statusbar.rowconfigure(0, weight=1)


def tick():
    # timeSV.set(time.strftime('%H:%M'))
    # widgets.statusbarLabelTime.after(1000*60, tick)
    timeSV.set(time.strftime('%H:%M:%S'))
    widgets.statusbarLabelTime.after(1000, tick)


tick()

# -------------------------------------------------------------------------------------------- #
# ----------------------------------- Runtime ------------------------------------------------ #
# -------------------------------------------------------------------------------------------- #

root.mainloop()
