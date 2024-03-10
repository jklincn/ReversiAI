import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# Import the tcl file
root.tk.call('source', 'Forest-ttk-theme/forest-light.tcl')

# Set the theme with the theme_use method
ttk.Style().theme_use('forest-light')

# A themed (ttk) button
button = ttk.Button(root, text="I'm a themed button")
button.pack(pady=20)

root.mainloop()