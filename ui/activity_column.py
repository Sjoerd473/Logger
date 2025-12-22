import tkinter as tk
from tkinter import messagebox, ttk

import psycopg


class ActivityColumn(ttk.Frame):
    def __init__(
        self,
        master,
        parent,
        db,
        project_col,
        sub_col,
        error_row,
        show_add_controls=True,
        show_all=False,
    ):
        super().__init__(master, padding=(12, 12, 12, 12))
        self.parent = parent
        self.db = db
        self.project_col = project_col
        self.subproject_col = sub_col
        self.error_row = error_row
        self.show_add_controls = show_add_controls
        self.show_all = show_all

        self.a_var = tk.StringVar()
        self.as_var = tk.StringVar()

        self._build_activity_column()
        self._bind_activity_events()

    # -----------------------------
    # ACTIVITY COLUMN UI
    # -----------------------------

    def _build_activity_column(self):
        self.grid(column=2, row=0)

        self.a_lbl = ttk.Label(self, text="Activity:")
        self.a_lbl.grid(column=0, row=0)

        self.a_list = tk.Listbox(self, listvariable=self.a_var, exportselection=False)
        self.a_list.grid(column=0, row=1, rowspan=5)

        if self.show_add_controls:
            self.ae_lbl = ttk.Label(self, text="Add a new activity")
            self.ae_lbl.grid(column=0, row=7)

            self.ae_ety = ttk.Entry(self)
            self.ae_ety.grid(column=0, row=8)

            self.ae_btn = ttk.Button(self, text="Add", command=self.add_activity)
            self.ae_btn.grid(column=0, row=9)
        else:
            self.au_lbl = ttk.Label(self, text="Toggle activity")
            self.au_lbl.grid(column=0, row=7)

            self.au_btn = ttk.Button(self, text="Update", command=self.update_activity)
            self.au_btn.grid(column=0, row=9)

    # -----------------------------
    # ACTIVITY COLUMN EVENTS
    # -----------------------------

    def _bind_activity_events(self):
        self.a_list.bind("<<ListboxSelect>>", self.update_status)

    # -----------------------------
    # ACTIVITY COLUMN LOGIC
    # -----------------------------
    #
    def update_status(self, event):
        p_name = self.project_col.get_selected_project()
        s_name = self.subproject_col.get_selected_subproject()
        a_name = self.get_selected_activity()

        if a_name:
            self.refresh_status(p_name, s_name, a_name)

    def add_activity(self):
        s_name = self.subproject_col.get_selected_subproject()
        p_name = self.project_col.get_selected_project()

        if s_name:
            s_acts = [item["name"] for item in self.db.get_acts(p_name, s_name)]
            a_name = self.ae_ety.get().strip()
            if a_name in s_acts:
                self.error_row.show_error(f"{a_name} already in database!")
            elif len(a_name) == 0:
                self.error_row.show_error("Invalid name")
            else:
                try:
                    self.ae_ety.delete(0, tk.END)
                    self.db.post_act(a_name, p_name, s_name)
                    self.refresh(p_name, s_name)
                except psycopg.IntegrityError:
                    self.db.conn.rollback()
                    messagebox.showerror(
                        "Duplicate Activity",
                        f"Subproject '{s_name}' already has an activity named '{a_name}'.",
                    )
                except Exception as e:
                    self.db.conn.rollback()
                    messagebox.showerror("Database Error", str(e))
        else:
            self.error_row.show_error("Select a subproject first")

    def update_activity(self):
        p_name = self.project_col.get_selected_project()
        s_name = self.subproject_col.get_selected_subproject()
        a_name = self.get_selected_activity()

        if a_name:
            try:
                self.db.update_activity(p_name, s_name, a_name)
                self.refresh_status(p_name, s_name, a_name)
            except psycopg.IntegrityError:
                self.db.conn.rollback()
                messagebox.showerror(
                    "Duplicate Activity",
                    f"Subproject '{s_name}' already has an activity named '{a_name}'.",
                )
            except Exception as e:
                self.db.conn.rollback()
                messagebox.showerror("Database Error", str(e))
        else:
            self.error_row.show_error("Select an activity first")

    def get_selected_activity(self):
        selection = self.a_list.curselection()
        if selection:
            return self.a_list.get(selection[0])

    def refresh(self, project, subproject):
        if self.show_all:
            acts = [item["name"] for item in self.db.get_all_acts(project, subproject)]
        else:
            acts = [item["name"] for item in self.db.get_acts(project, subproject)]
        self.a_var.set(acts)

    def refresh_status(self, project, subproject, activity):
        project_id = self.db.get_project_id(project)
        subproject_id = self.db.get_subproject_id(subproject, project_id)
        activity_status = self.db.get_activity_status(
            project_id, subproject_id, activity
        )
        if activity_status == 1:
            activity_status = "Finished"
        else:
            activity_status = "Not finished"
        self.as_var.set(activity_status)

    def reset(self):
        self.a_var.set([])
