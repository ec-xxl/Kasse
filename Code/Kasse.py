import sqlite3
import tkinter as tk

master = tk.Tk()
selectedTeam = tk.StringVar()


def add_player(team: str):
    popup = tk.Tk()
    popup.attributes("-topmost", True)
    e = tk.Entry(popup)
    e.pack()

    def callback():
        player = e.get()  # This is the text you may want to use later
        insert_player = "INSERT INTO players (player_name, team_name) VALUES (?, ?)"  # SQL-String
        runQuery(insert_player, (player, team))  # add to Database
        listbox.insert(tk.END, player)  # add to Listbox
        popup.destroy()

    popupb = tk.Button(popup, text="OK", width=10, command=callback)
    popupb.pack()

    popup.mainloop()


def get_players(team: str):
    select_player = "SELECT player_name FROM players WHERE team_name = ?"
    players = runQuery(select_player, (team,), receive=tk.TRUE)
    return players


def onSelectTeam():
    listbox.delete(0, tk.END)
    players = get_players(getSelectedTeam())
    for player in players:
        listbox.insert(tk.END, player)


def getSelectedTeam():
    # TODO: delete print statements
    print(selectedTeam.get())
    print("happily I announce that this is the expected result")
    # TODO: unselect Team
    return selectedTeam.get()


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


# Player
# delete_table = "DROP TABLE IF EXISTS players"
# runQuery(delete_table)
create_table = "CREATE TABLE IF NOT EXISTS players(id integer primary key autoincrement, player_name text, team_name text)"
runQuery(create_table)

# get teams from the teams.txt file
f = open("teams.txt", "r")
teamList = f.readlines()
f.close()

# create Radiobutton for each Team in TeamList
for team in teamList:
    [name, pos] = team.split(";")
    b = tk.Radiobutton(master, text=name, command=lambda: onSelectTeam(), variable=selectedTeam, value=name, indicatoron=0)
    b.grid(column=int(pos) % 4, row=int(pos) // 4)

# create Listbox for player names
listbox = tk.Listbox(master)
listbox.grid(column=5, row=0, rowspan=3, columnspan=2)

# TODO: Add check if a Team is selected. If not create info to select team
b = tk.Button(master, text="Add Player", command=lambda: add_player(getSelectedTeam()))
b.grid(row=4, column=5)
tButton = tk.Button(master, text="Test")
tButton.grid(column=6, row=4)
master.mainloop()
