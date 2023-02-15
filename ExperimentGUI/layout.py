from tkinter import *  # pyright: ignore (this is tkinter style)
from tkinter import font
from tkinter import ttk

root = Tk()
root.title('Control layout')

tl = Toplevel(root)
tl.title('Experiment layout')
tl.geometry('1920x1080')
tl.attributes('-fullscreen', True)

mainframe = ttk.Frame(tl, padding='6 6 24 24')
mainframe.grid(column=0, row=0, sticky='nwes')
tl.columnconfigure(0, weight=1)
tl.rowconfigure(0, weight=1)

family = font.nametofont('TkTextFont').actual()['family']
bigFont = font.Font(family=family, size=50, weight='normal')
statustext = StringVar()
statustext.set('Now this is happening')
ttk.Label(mainframe, textvariable=statustext,
          font=bigFont).grid(column=1, row=1, sticky='nw')
mainframe.rowconfigure(1, weight=1)
ttk.Label(
    mainframe, text='Click right mouse button to quit', font=bigFont).grid(column=1, row=2, sticky='sw')
cycletext = StringVar()
cycletext.set('Cycles completed: 12')
ttk.Label(mainframe, textvariable=cycletext, font=bigFont).grid(column=1, row=3, sticky='sw')

root.mainloop()

