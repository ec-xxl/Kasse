import os
from functools import partial
from tkinter import *
import sqlite3


master = Tk()
selectedTeam = StringVar()
selectedItems = {}


def add_player(team: str):
    popup = Tk()
    popup.attributes("-topmost", True)
    e = Entry(popup)
    e.pack()
    e.focus()
    os.system("osk")

    def callback():
        player = e.get()  # This is the text you may want to use later
        insert_player = "INSERT INTO players (player_name, team_name) VALUES (?, ?)"    # SQL-String
        runQuery(insert_player, (player, team))     # add to Database
        listbox_player.insert(END, player)    # add to Listbox
        popup.destroy()

    popButton = Button(popup, text="OK", width=10, command=callback)
    popButton.pack()

    popup.mainloop()


def get_players(team: str):
    select_player = "SELECT player_name FROM players WHERE team_name = ?"
    players = runQuery(select_player, (team,), receive=TRUE)
    return players


def onSelectTeam():
    listbox_player.delete(0, END)
    players = get_players(getSelectedTeam())
    for player in players:
        listbox_player.insert(END, player)


def getSelectedTeam():
    return selectedTeam.get()

def displayOrder(d=selectedItems):
    listbox_order.delete(0,END)
    for item in d:
        listbox_order.insert(END, (item[0], item[1], d[item]))

def onClickItem(name: str, price:float):
    if (name, price) not in selectedItems:
        selectedItems[(name, price)] = 0
    selectedItems[(name, price)] += 1
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
create_table_order = "CREATE TABLE IF NOT EXISTS purchases(id integer primary key autoincrement, player_id integer, item_name text, item_quantity integer, price numeric, payed boolean default false)"
runQuery(create_table_order)

# get teams from the teams.txt file
f = open("teams.txt", "r")
teamList = f.readlines()
f.close()
# Radiobutton for each Team in TeamList
for team in teamList:
    [name, pos] = team.strip().split(";")
    b = Radiobutton(master, text=name, command=lambda: onSelectTeam(), variable=selectedTeam, value=name, indicatoron=0)
    b.grid(column=int(pos) % 4, row=int(pos) // 4)

# Label for Food
Label(master, text="Essen").grid(column=7, columnspan=2, row=0)

# Button for each Food in FoodList
f = open("food.txt", "r")
foodList = f.readlines()
f.close()
for food in foodList:
    [name, price, pos] = food.strip().split(";")
    b = Button(master, text=name+"\n"+price+"€", command=partial(onClickItem, name, float(price)))
    b.grid(column=int(pos) % 3 + 7, row=int(pos) // 3 + 1)


# List of Players in a Team
listbox_player = Listbox(master)
listbox_player.grid(column=5, row=0, rowspan=3, columnspan=2)

# List of Items in Order
listbox_order = Listbox(master)
listbox_order.grid(column=10, row=0, rowspan=3, columnspan=2)



# TODO: Add check if a Team is selected. If not create info to select team
b = Button(master, text="Add Player", command=lambda: add_player(getSelectedTeam()))
b.grid(row=4, column=5)
tButton = Button(master, text="Test")
tButton.grid(column=6, row=4)
master.mainloop()
