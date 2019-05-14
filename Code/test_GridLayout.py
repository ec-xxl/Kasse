import tkinter as tk
from types import SimpleNamespace


window = SimpleNamespace()
window.root = tk.Tk()
window.root.title("Südsee Cup Kasse")


window.root.frame = SimpleNamespace()

window.root.frame.main = tk.Frame(window.root, width=450, height=500, bg="red")
window.root.frame.statusbar = tk.Frame(window.root, width=450, height=50, bg="yellow")

tk.Label(window.root.frame.main, text='Main').pack(expand=1, fill=tk.X)
tk.Label(window.root.frame.statusbar, text='Status bar').pack(expand=1, fill=tk.BOTH)

window.root.frame.main.grid(row=0, sticky="nsew")
window.root.frame.statusbar.grid(row=1, sticky="nsew")

window.root.grid_rowconfigure(1, weight=1)
window.root.grid_columnconfigure(1, weight=1)

# # menu left
# menu_left = tk.Frame(root, width=150, bg="#ababab")
# menu_left_upper = tk.Frame(menu_left, width=150, height=150, bg="red")
# menu_left_lower = tk.Frame(menu_left, width=150, bg="blue")
#
# test = tk.Label(menu_left_upper, text="test")
# test.pack()
#
#
# menu_left_upper.pack(side="top", fill="both", expand=True)
# menu_left_lower.pack(side="top", fill="both", expand=True)
#
# # right area
# some_title_frame = tk.Frame(root, bg="#dfdfdf")
#
# some_title = tk.Label(some_title_frame, text="some title", bg="#dfdfdf")
# some_title.pack()
#
# canvas_area = tk.Canvas(root, width=500, height=400, background="#ffffff")
# canvas_area.grid(row=1, column=1)
#
# # status bar
# status_frame = tk.Frame(root)
# status = tk.Label(status_frame, text="this is the status bar")
# status.pack(fill="both", expand=True)
#
# menu_left.grid(row=0, column=0, rowspan=2, sticky="nsew")
# some_title_frame.grid(row=0, column=1, sticky="ew")
# canvas_area.grid(row=1, column=1, sticky="nsew")
# status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
#
# root.grid_rowconfigure(1, weight=1)
# root.grid_columnconfigure(1, weight=1)

window.root.mainloop()