import tkinter as tk
from tkinter import ttk

from modules.activity_column import ActivityColumn
from modules.button_column import PaymentColumn
from modules.db import LoggerDB
from modules.project_column import ProjectColumn
from modules.row_writer import Add_row
from modules.sub_column import SubprojectColumn

dsn = "dbname=logger user=postgres password=megablaat"


# layout sizing and positioning,

# window to mark things complete

#
# another class for a mark for complete window
#


class App:
    def __init__(self, root):
        self.root = root
        self.db = LoggerDB(dsn)
        self.new_row = Add_row()

        self.error_var = tk.StringVar()

        self.project_col = ProjectColumn(
            root,
            self,
            self.db,
            self.on_project_selected,
            self.show_error,
        )
        self.subproject_col = SubprojectColumn(
            root,
            self,
            self.db,
            self.on_subproject_selected,
            self.show_error,
        )
        self.activity_col = ActivityColumn(root, self, self.db, self.show_error)
        self.payment_col = PaymentColumn(
            root, self, self.db, self.new_row, self.show_error
        )

        self._build_error_label()

        self.project_col.refresh()

    def _build_error_label(self):
        self.error_lbl = ttk.Label(
            self.root, textvariable=self.error_var, foreground="red"
        )
        self.error_lbl.grid(column=0, row=1, columnspan=3)

    def show_error(self, msg):
        self.error_var.set(msg)
        self.root.after(5000, lambda: self.error_var.set(""))

    def refresh_listbox(self, cat, project=None, subproject=None):
        if cat == "p":
            self.project_col.refresh()
        elif cat == "s":
            self.subproject_col.refresh(project)
        elif cat == "a":
            self.activity_col.refresh(subproject)

    def on_project_selected(self, project_name):
        self.subproject_col.refresh(project_name)

    def on_subproject_selected(self, project, subproject):
        self.activity_col.refresh(project, subproject)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
