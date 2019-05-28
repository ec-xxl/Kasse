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


def add_player(team: str):
    popup = tk.Tk()
    popup.attributes("-topmost", True)
    e = tk.Entry(popup)
    e.pack()
    e.focus()
    os.system("osk")

    def callback():
        player = e.get()  # This is the text you may want to use later
        insert_player = "INSERT INTO players (player_name, team_name) VALUES (?, ?)"    # SQL-String
        runQuery(insert_player, (player, team))     # add to Database
        displayPlayers(team)    # add to Listbox
        popup.destroy()

    popButton = tk.Button(popup, text="OK", width=10, command=callback)
    popButton.pack()

    popup.mainloop()


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
        listbox_player.insert(tk.END, player+str(player_id))

def displayOrder():
    listbox_order.delete(0,tk.END)
    for item in selectedItems:
        listbox_order.insert(tk.END, item[0]+" "+str(item[1])+"€ x "+str(selectedItems[item]))
    updateTotal()

def onClickItem(name: str, price:float):
    if (name, price) not in selectedItems:
        selectedItems[(name, price)] = 0
    selectedItems[(name, price)] += 1
    displayOrder()




def getSelectedPlayerID():
    #TODO: catch Error if no player selected
    pos = listbox_player.curselection()
    return displayedPlayers[pos][0]

def confirmOrder():
    global selectedItems
    player_id = getSelectedPlayerID()
    if player_id:
        for item in selectedItems:
            insert_order = "INSERT INTO purchases (player_id, item_name, price, item_quantity, payed) VALUES (?, ?, ?, ?, ?)"
            data = (player_id[0], item[0], item[1], selectedItems[item], 0)
            runQuery(insert_order, data)
        selectedItems = {}
        displayOrder()
        #TODO: else display Select Player


def stornoOrder():
    global selectedItems
    player_id = getSelectedPlayerID()
    if player_id:
        for item in selectedItems:
            insert_order = "INSERT INTO purchases (player_id, item_name, price, item_quantity, payed) VALUES (?, ?, ?, ?, ?)"
            data = (player_id[0], item[0], item[1], -selectedItems[item], 0)
            runQuery(insert_order, data)
        selectedItems = {}
        displayOrder()
        # TODO: else display Select Player --- same as confirmOrder


def deleteOrder():
    global selectedItems
    selectedItems = collections.OrderedDict()
    displayOrder()


def onSelectOrder(evt):
    global selectedItems
    w = evt.widget
    if w.curselection is not ():
        idx = int(w.curselection()[0])
        key = list(selectedItems.keys())[idx]
        quantity = selectedItems[key] - 1
        selectedItems[key] = quantity
        if quantity == 0:
            del selectedItems[list(selectedItems.keys())[idx]]
        displayOrder()



def updateTotal():
    global totalSV
    total = 0
    for item in selectedItems:
        total += item[1]*selectedItems[item]
    totalSV.set("%.2f €" % total)





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


delete_table = "DROP TABLE IF EXISTS purchases"
runQuery(delete_table)

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
# TODO: Add check if a Team is selected. If not create info to select team
b = tk.Button(playerFrame, text="Add Player", command=lambda: add_player(getSelectedTeam()))
b.grid(column=0, row=1)


def test():
    listbox_player.insert(tk.END, ("Test1", "Test2", "Test3"))
    listbox_player.setvar("42")


tButton = tk.Button(playerFrame, text="Test", command=lambda: test())
tButton.grid(column=1, row=1)


orderFrame = tk.Frame(master)
orderFrame.grid(column=4, row=0)
# List of Items in Order
listbox_order = tk.Listbox(orderFrame)
listbox_order.grid(column=0, row=0)
listbox_order.bind('<<ListboxSelect>>', onSelectOrder)

# Optionen auf OrderFrame
tk.Button(orderFrame, text="Stornieren", command=stornoOrder).grid(column=0, row=3)
tk.Button(orderFrame, text="Auswahl löschen", command=deleteOrder).grid(column=0, row=4)
tk.Button(orderFrame, text="Buchung bestätigen", command=confirmOrder).grid(column=0, row=5)

# Summe des Kaufes
totalLabel = tk.Label(orderFrame, textvariable=totalSV).grid(column=0, row=2)

treeFrame = tk.Frame(master)
treeFrame.grid(column=6, row=0)
tree = ttk.Treeview(treeFrame)
tree["columns"]=("Preis", "Anzahl")
tree.heading("0",  text="Bestellung")
tree.heading("Preis", text="Preis", anchor=tk.W)
tree.heading("Anzahl", text="Anzahl", anchor=tk.W)


# Level 2
photo = tk.PhotoImage(file="minus-8-64.gif")
tree.insert("", "end", image=photo, text="Salat", values=("23-Jun-17 11:28", "PNG file"))
tree.insert("", "end", text="Schnitzel", values=("23-Jun-17 11:29", "PNG file"))
tree.insert("", "end", text="Hilfe", values=("23-Jun-17 11:30", "PNG file"))


tree.pack(side=tk.TOP)

master.mainloop()
