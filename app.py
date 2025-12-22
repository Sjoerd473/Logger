import tkinter as tk
from tkinter import ttk

from db.db import LoggerDB
from ui.activity_column import ActivityColumn
from ui.error_row import ErrorRow
from ui.project_column import ProjectColumn
from ui.row_writer import Add_row
from ui.side_column import SideColumn
from ui.sub_column import SubprojectColumn

dsn = "dbname=logger user=postgres password=megablaat"


# layout sizing and positioning,
# containerize? move the DSN data?


class App:
    def __init__(self, root):
        self.root = root
        self.db = LoggerDB(dsn)
        self.new_row = Add_row()
        self.error_row = ErrorRow(root)
        self.root.geometry("+200+60")
        self.root.title("Logger")

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
        self.payment_col = SideColumn(
            root,
            self,
            self.db,
            self.project_col,
            self.subproject_col,
            self.activity_col,
            self.new_row,
            self.error_row,
        )

        self.error_row.grid(column=0, row=10)

        self._build_modify_btn()

        self.project_col.refresh()

    def on_project_selected(self, project_name):
        self.subproject_col.refresh(project_name)

    def on_subproject_selected(self, project, subproject):
        self.activity_col.refresh(project, subproject)

    def _build_modify_btn(self):
        self.modify_btn = ttk.Button(
            self.root, text="Modify projects", command=self.open_modify_window
        )
        self.modify_btn.grid(column=1, row=2, columnspan=2, sticky="we")

    def open_modify_window(self):
        win = tk.Toplevel(self.root)
        win.title("Project Settings")
        win.geometry("700x250+200+460")

        error_row = ErrorRow(win)
        error_row.grid(column=2, row=5, columnspan=3)

        def on_close():
            self.project_col.refresh()
            self.subproject_col.reset()
            self.activity_col.reset()

            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

        def on_project_selected_local(project_name):
            subproject_col.refresh(project_name)
            project_col.refresh_status(project_name)

        def on_subproject_selected_local(project_name, subproject_name):
            activity_col.refresh(project_name, subproject_name)
            subproject_col.refresh_status(project_name, subproject_name)

        # def on_activity_selected_local(project_name, subproject_name, activity_name):
        #     activity_col.refresh(project_name, subproject_name)
        #     activity_col.refresh_status(project_name, subproject_name, activity_name)

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
        side_col = SideColumn(
            win,
            self,
            self.db,
            project_col,
            subproject_col,
            activity_col,
            self.new_row,
            error_row,
            False,
        )
        side_col.grid(column=3, row=0)

        project_col.refresh()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
