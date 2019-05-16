import tkinter as tk

class TextScrollXY(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent)
        self.text = tk.Text(self, *args, **kwargs)
        # vertical scrollbar
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        # horizontal scrollbar
        self.hsb = tk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.text.configure(xscrollcommand=self.hsb.set)
        self.hsb.pack(side="bottom", fill="x")
        # text option
        self.text.pack(side="left", fill="both", expand=True)
        self.text.configure(wrap="none")

class FrameScrollXY(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent)
        self.canv = tk.Canvas(self, *args, **kwargs)
        #vertical scrollbar
        self.vsb = tk.Scrollbar(self, orient="vertical")
        self.canv.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.vsb.configure(command=self.canv.yview)
        #horizontal scrollbar
        self.hsb = tk.Scrollbar(self, orient="horizontal")
        self.canv.configure(yscrollcommand=self.hsb.set)
        self.hsb.pack(side="bottom", fill="x")
        self.hsb.configure(command=self.canv.xview)
        #text option

# class Example(tk.Frame):
#     def __init__(self, parent):
#         tk.Frame.__init__(self, parent)
#         self.scrolled_text = TextScrollXY(self)
#         self.scrolled_text.pack(side="top", fill="both", expand=True)
#         with open(__file__, "r") as f:
#             self.scrolled_text.text.insert("1.0", f.read())

class Example(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.CustomWidget = FrameScrollXY(self)
        self.CustomWidget.pack(side="top", fill="both", expand=True)

root = tk.Tk()
Example(root).pack(side="top", fill="both", expand=True)
root.mainloop()