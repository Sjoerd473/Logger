import tkinter as tk
from tkinter import ttk

from modules.activity_column import ActivityColumn
from modules.db import LoggerDB
from modules.error_row import ErrorRow
from modules.project_column import ProjectColumn
from modules.row_writer import Add_row
from modules.side_column import SideColumn
from modules.sub_column import SubprojectColumn

dsn = "dbname=logger user=postgres password=megablaat"


# layout sizing and positioning,

# window to mark things complete, error handling, a side window with information on the project


#
# closing update window refreshes main window, it now resets the columns, only refreshes projects
#


class App:
    def __init__(self, root):
        self.root = root
        self.db = LoggerDB(dsn)
        self.new_row = Add_row()
        self.error_row = ErrorRow(root)

        self.error_var = tk.StringVar()

        self.project_col = ProjectColumn(
            root,
            self,
            self.db,
            self.on_project_selected,
            self.error_row,
        )
        self.subproject_col = SubprojectColumn(
            root,
            self,
            self.db,
            self.project_col,
            self.on_subproject_selected,
            self.error_row,
        )
        self.activity_col = ActivityColumn(
            root, self, self.db, self.project_col, self.subproject_col, self.error_row
        )
        self.payment_col = SideColumn(root, self, self.db, self.new_row, self.error_row)

        self.error_row.grid(column=0, row=10)

        self._build_modify_btn()

        self.project_col.refresh()

    # def _build_error_label(self):
    #     self.error_lbl = ttk.Label(
    #         self.root, textvariable=self.error_var, foreground="red"
    #     )
    #     self.error_lbl.grid(column=0, row=1, columnspan=3)

    # def show_error(self, msg):
    #     self.error_var.set(msg)
    #     self.root.after(5000, lambda: self.error_var.set(""))

    def _build_modify_btn(self):
        self.modify_btn = ttk.Button(
            self.root, text="Modify projects", command=self.open_modify_window
        )
        self.modify_btn.grid(column=1, row=2, columnspan=2, sticky="we")

    def open_modify_window(self):
        win = tk.Toplevel(self.root)
        win.title("Project Settings")

        error_row = ErrorRow(win)
        error_row.grid(column=2, row=5, columnspan=3)

        def on_close():
            # refresh whatever you need in the main window
            self.project_col.refresh()
            self.subproject_col.reset()
            self.activity_col.reset()
            # then destroy the window
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

        def on_project_selected_local(project_name):
            subproject_col.refresh(project_name)

        def on_subproject_selected_local(project_name, subproject_name):
            activity_col.refresh(project_name, subproject_name)

        project_col = ProjectColumn(
            win,
            self,
            self.db,
            on_project_selected_local,
            error_row,
            False,  # hides buttons
            True,  # toggle for all projects from DB
        )
        project_col.grid(column=0, row=0)

        subproject_col = SubprojectColumn(
            win,
            self,
            self.db,
            project_col,
            on_subproject_selected_local,
            error_row,
            False,
            True,
        )
        subproject_col.grid(column=1, row=0)

        activity_col = ActivityColumn(
            win,
            self,
            self.db,
            project_col,
            subproject_col,
            error_row,
            False,
            True,
        )

        activity_col.grid(column=2, row=0)

        project_col.refresh()

    def on_project_selected(self, project_name):
        self.subproject_col.refresh(project_name)

    def on_subproject_selected(self, project, subproject):
        self.activity_col.refresh(project, subproject)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
