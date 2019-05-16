import os
from functools import partial
import tkinter as tk
import sqlite3
import tkinter as tk

master = tk.Tk()
selectedTeam = tk.StringVar()

master = tk.Tk()
selectedTeam = tk.StringVar()
selectedItems = {}

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
        listbox_player.insert(tk.END, player)    # add to Listbox
        popup.destroy()

    popButton = tk.Button(popup, text="OK", width=10, command=callback)
    popButton.pack()

    popup.mainloop()


def get_players(team: str):
    select_player = "SELECT player_name FROM players WHERE team_name = ?"
    players = runQuery(select_player, (team,), receive=tk.TRUE)
    return players


def onSelectTeam():
    listbox_player.delete(0, tk.END)
    players = get_players(getSelectedTeam())
    for player in players:
        listbox_player.insert(tk.END, player)


def getSelectedTeam():
    return selectedTeam.get()

def displayOrder():
    listbox_order.delete(0,tk.END)
    for item in selectedItems:
        listbox_order.insert(tk.END, (item[0], item[1], selectedItems[item]))

def onClickItem(name: str, price:float):
    if (name, price) not in selectedItems:
        selectedItems[(name, price)] = 0
    selectedItems[(name, price)] += 1
    displayOrder()

def getSelectedPlayerID():
    return listbox_player.get(tk.ACTIVE)

def confirmOrder():
    player_id = getSelectedPlayerID()
    global selectedItems
    if player_id:
        for item in selectedItems:
            insert_order = "INSERT INTO purchases (player_id, item_name, price, item_quantity, payed) VALUES (?, ?, ?, ?, ?)"
            data = (player_id, item[0], item[1], selectedItems[item], 0)
            runQuery(insert_order, data)
            selectedItems = {}
            displayOrder()





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


# delete_table = "DROP TABLE IF EXISTS players"

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
    b = tk.Radiobutton(teamFrame, text=name, command=lambda: onSelectTeam(), variable=selectedTeam, value=name, indicatoron=0)
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
playerFrame.grid(column=1,row=0)
# List of Players in a Team
listbox_player = tk.Listbox(playerFrame)
listbox_player.grid(column=0, row=0, columnspan=2)
# TODO: Add check if a Team is selected. If not create info to select team
b = tk.Button(playerFrame, text="Add Player", command=lambda: add_player(getSelectedTeam()))
b.grid(column=0, row=1)
tButton = tk.Button(playerFrame, text="Test")
tButton.grid(column=1, row=1)


orderFrame = tk.Frame(master)
orderFrame.grid(column=4, row=0)
# List of Items in Order
listbox_order = tk.Listbox(orderFrame)
listbox_order.grid(column=0, row=0)

b = tk.Button(orderFrame, text="Buchung bestätigen", command=lambda: confirmOrder())
b.grid(column=0, row=1)


master.mainloop()
