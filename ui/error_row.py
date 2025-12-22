import tkinter as tk
from tkinter import ttk


class ErrorRow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.error_var = tk.StringVar()

        self.error_lbl = ttk.Label(self, textvariable=self.error_var, foreground="red")
        self.error_lbl.grid(column=0, row=0, sticky="w")

    def show_error(self, msg):
        self.error_var.set(msg)
        self.after(5000, lambda: self.error_var.set(""))
