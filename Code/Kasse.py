import collections
import os
from functools import partial
import tkinter as tk
import sqlite3
from tkinter import ttk

master = tk.Tk()
selectedTeam = tk.StringVar()
selectedItems = collections.OrderedDict()
displayedPlayers = []
totalSV = tk.StringVar()
totalSV.set("0.00 €")


def popupError(s):
    popupRoot = tk.Tk()
    popupRoot.after(2000, lambda: popupRoot.destroy())          # Time in Miliseconds 2000 = 2 seconds
    popupButton = tk.Button(popupRoot, text=s, font=("Verdana", 12), bg="yellow", command=lambda: popupRoot.destroy())
    popupButton.pack()
    popupRoot.geometry('400x50+700+500')
    popupRoot.mainloop()

def add_player():
    def callback():
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
        popup.mainloop()
    else:
        popupError("Bitte ein Team auswählen")


def get_players(team: str):
    select_player = "SELECT id, player_name FROM players WHERE team_name = ?"
    players = runQuery(select_player, (team,), receive=tk.TRUE)
    return players


def onSelectTeam(team: str):
    displayPlayers(team)


def getSelectedTeam():
    return selectedTeam.get()


def displayPlayers(team: str):
    listbox_player.delete(0, tk.END)
    players = get_players(team)
    global displayedPlayers
    displayedPlayers = players
    for player_id, player in players:
        listbox_player.insert(tk.END, player)

def displayOrder():
    orders = tree.get_children()
    if orders != '()':
        for order in orders:
            tree.delete(order)
    for item in selectedItems:
        tree.insert("", "end", text=item[0], values=("%.2f€" % item[1], str(selectedItems[item]), "%.2f€" % (item[1]*selectedItems[item])), tags=item)
    updateTotal()

def onClickItem(name: str, price:float):
    if (name, price) not in selectedItems:
        selectedItems[(name, price)] = 0
    selectedItems[(name, price)] += 1
    displayOrder()

def getSelectedPlayerID():
    if listbox_player.curselection():
        pos = listbox_player.curselection()[0]
        return displayedPlayers[pos][0]
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


def onSelectOrder(evt):
    global selectedItems
    curItem = tree.focus()
    item = tree.item(curItem)
    key = (item.get('tags')[0], float(item.get('tags')[1]))
    quantity = selectedItems[key] - 1
    selectedItems[key] = quantity
    if quantity == 0:
        del selectedItems[key]
    displayOrder()


def updateTotal():
    global totalSV
    total = 0
    for item in selectedItems:
        total += item[1]*selectedItems[item]
    totalSV.set("Summe: %.2f €" % total)


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


        popButton = tk.Button(popPay, text="Abrechnen", width=10, command=deduction)
        popButton.grid(column=0, row=2)
        popPay.mainloop()





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


# delete_table = "DROP TABLE IF EXISTS purchases"
# runQuery(delete_table)

# create Player Table
create_table_players = "CREATE TABLE IF NOT EXISTS players(id integer primary key autoincrement, player_name text, team_name text)"
runQuery(create_table_players)

# create Order Table
create_table_order = "CREATE TABLE IF NOT EXISTS purchases(id integer primary key autoincrement, player_id integer, item_name text, item_quantity integer, price numeric, payed integer default 0)"
runQuery(create_table_order)

# get teams from the teams.txt file
f = open("teams.txt", "r")
teamList = f.readlines()
f.close()


teamFrame = tk.Frame(master)
teamFrame.grid(column=0, row=0, rowspan=2)

# Radiobutton for each Team in TeamList
for team in teamList:
    [name, pos] = team.strip().split(";")
    b = tk.Radiobutton(teamFrame, text=name, command=partial(onSelectTeam, name), variable=selectedTeam, value=name, indicatoron=0)
    b.grid(column=int(pos) % 4, row=int(pos) // 4)

itemFrame = tk.Frame(master)
itemFrame.grid(column=3, row=0)

# Label for Food
tk.Label(itemFrame, text="Essen").grid(column=0, row=0)

# Button for each Food in FoodList
f = open("food.txt", "r")
foodList = f.readlines()
f.close()
for food in foodList:
    [name, price, pos] = food.strip().split(";")
    b = tk.Button(itemFrame, text=name+"\n"+price+"€", command=partial(onClickItem, name, float(price)))
    b.grid(column=int(pos) % 3, row=int(pos) // 3 + 1)

playerFrame = tk.Frame(master)
playerFrame.grid(column=1, row=0)
# List of Players in a Team
listbox_player = tk.Listbox(playerFrame)
listbox_player.grid(column=0, row=0, columnspan=2)
b = tk.Button(playerFrame, text="Add Player", command=add_player)
b.grid(column=0, row=1)
tButton = tk.Button(playerFrame, text="Test")
tButton.grid(column=1, row=1)


orderFrame = tk.Frame(master)
orderFrame.grid(column=4, row=0)

# Optionen auf OrderFrame
tk.Button(orderFrame, text="Spieler abrechnen", command=popupPay).grid(column=0, row=3)
tk.Button(orderFrame, text="Buchung stornieren", command=stornoOrder).grid(column=0, row=4)
tk.Button(orderFrame, text="Auswahl löschen", command=deleteOrder).grid(column=0, row=5)
tk.Button(orderFrame, text="Buchung bestätigen", command=confirmOrder).grid(column=0, row=6)

# Summe des Kaufes
totalLabel = tk.Label(orderFrame, textvariable=totalSV).grid(column=0, row=2)


tree = ttk.Treeview(orderFrame)
tree["columns"]=("Preis", "Anzahl", "Gesammt")
tree.heading("0",  text="Bestellung")
tree.heading("Preis", text="Preis", anchor=tk.W)
tree.heading("Anzahl", text="Anzahl", anchor=tk.W)
tree.bind('<<TreeviewSelect>>', onSelectOrder)

tree.grid(column=0, row=0)

master.mainloop()
