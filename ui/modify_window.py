import tkinter as tk
from tkinter import ttk

from ui.activity_column import ActivityColumn
from ui.error_row import ErrorRow
from ui.project_column import ProjectColumn
from ui.side_column import SideColumn
from ui.sub_column import SubprojectColumn

class ModifyWindow:
    def __init__(self, root, parent, project, subproject, activity, error_row, add_row, file_writer, db, show_update_button=True, show_toggle_controls=True, show_add_to_db_menu=False):
        self.root = root
        self.parent = parent
        self.project = project
        self.subproject = subproject
        self.activity = activity
        self.error_row = error_row
        self.new_row = add_row # This is superfluous?
        self.file_writer = file_writer
        self.db = db
        self.show_update_button = show_update_button
        self.show_toggle_controls = show_toggle_controls

        self.modify_window = tk.Toplevel(self.root)
        self.modify_window.geometry("700x250+200+460")
        self.modify_window.title("Modify data")

        self._build_modify_frame()
        self.modify_window.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_modify_frame(self):
        self.project_col = ProjectColumn(
            self.modify_window,
            self,
            self.db,
            self.on_project_selected_local,
            self.error_row,
            False,  # hides buttons
            True,  # toggle for all projects from DB
            self.show_toggle_controls
        )
        self.project_col.grid(column=0, row=0)

        self.subproject_col = SubprojectColumn(
            self.modify_window,
            self,
            self.db,
            self.project_col,
            self.on_subproject_selected_local,
            self.error_row,
            False,
            True,
            self.show_toggle_controls
        )
        self.subproject_col.grid(column=1, row=0)

        self.activity_col = ActivityColumn(
            self.modify_window,
            self,
            self.db,
            self.project_col,
            self.subproject_col,
            self.error_row,
            False,
            True,
            self.show_toggle_controls
        )
        self.activity_col.grid(column=2, row=0)
        self.side_col = SideColumn(
            self.modify_window,
            self,
            self.db,
            self.project_col,
            self.subproject_col,
            self.activity_col,
            self.new_row,
            self.error_row,
            False,
            self.show_update_button
        )
        self.side_col.grid(column=3, row=0)

        self.project_col.refresh()

    
    def on_close(self): #These are the columns of the parent/original window
            self.parent.project_col.refresh()
            self.parent.subproject_col.reset()
            self.parent.activity_col.reset()

            self.modify_window.destroy()
    def on_project_selected_local(self,project_name):
        self.subproject_col.refresh(project_name)
        self.project_col.refresh_status(project_name)

    def on_subproject_selected_local(self, project_name, subproject_name):
        self.activity_col.refresh(project_name, subproject_name)
        self.subproject_col.refresh_status(project_name, subproject_name)

          

