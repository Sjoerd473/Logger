import tkinter as tk
from tkinter import ttk

from db.db import LoggerDB
from modules.file_writer import FileWriter
from ui.row_writer import Add_row #This is in the wrong folder
from ui.activity_column import ActivityColumn
from ui.error_row import ErrorRow
from ui.project_column import ProjectColumn
from ui.side_column import SideColumn
from ui.sub_column import SubprojectColumn
from ui.modify_window import ModifyWindow


# a box to toggle fixed sum instead of hourly rate?



class App:
    def __init__(self, root):
        self.root = root
        self.db = LoggerDB()
        self.new_row = Add_row()
        self.file_writer = FileWriter()
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
        self._build_add_row_to_db_btn()

        self.project_col.refresh()

    def on_project_selected(self, project_name):
        self.subproject_col.refresh(project_name)

    def on_subproject_selected(self, project, subproject):
        self.activity_col.refresh(project, subproject)

    def _build_modify_btn(self):
        self.modify_btn = ttk.Button(
            self.root, text="Modify projects", command=self.open_modify_window
        )
        self.modify_btn.grid(column=2, row=2, columnspan=2, sticky="we")

    def _build_add_row_to_db_btn(self):
        self.add_row_to_db_btn = ttk.Button(
            self.root, text="Add row to DB", command=self.open_add_to_db_window
        )
        self.add_row_to_db_btn.grid(column=0, row=2, columnspan=2, sticky="we")
 

    def open_modify_window(self):
       ModifyWindow(root, self, self.project_col, self.subproject_col, self.activity_col, self.error_row, self.new_row, self.file_writer, self.db)
    
    def open_add_to_db_window(self):
          ModifyWindow(root, self, self.project_col, self.subproject_col, self.activity_col, self.error_row, self.new_row, self.file_writer, self.db, False, False)
    


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
