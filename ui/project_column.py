import tkinter as tk
from tkinter import messagebox, ttk

import psycopg


class ProjectColumn(ttk.Frame):
    def __init__(
        self,
        master,
        parent,
        db,
        on_project_selected,
        error_row,
        show_add_controls=True,
        show_all=False,
    ):
        super().__init__(master, padding=(12, 12, 12, 12))
        self.parent = parent
        self.db = db
        self.on_project_selected = on_project_selected
        self.error_row = error_row
        self.show_add_controls = show_add_controls
        self.show_all = show_all

        self._build_project_column()
        self._bind_project_events()

    # -----------------------------
    # PROJECT COLUMN UI
    # -----------------------------
    def _build_project_column(self):
        self.grid(column=0, row=0, sticky="nwes")

        self.p_var = tk.StringVar()
        self.ps_var = tk.StringVar()

        self.p_lbl = ttk.Label(self, text="Project:")
        self.p_lbl.grid(column=0, row=0)

        self.p_list = tk.Listbox(self, listvariable=self.p_var, exportselection=False)
        self.p_list.grid(column=0, row=1, rowspan=5)

        if self.show_add_controls:
            self.pe_lbl = ttk.Label(self, text="Add a new project")
            self.pe_lbl.grid(column=0, row=6)

            self.pe_ety = ttk.Entry(self)
            self.pe_ety.grid(column=0, row=7)

            self.pe_btn = ttk.Button(self, text="Add", command=self.add_project)
            self.pe_btn.grid(column=0, row=8)
        else:
            self.su_lbl = ttk.Label(self, text="Toggle project")
            self.su_lbl.grid(column=0, row=7)

            self.su_btn = ttk.Button(self, text="Update", command=self.update_project)
            self.su_btn.grid(column=0, row=9)

    # -----------------------------
    # PROJECT COLUMN EVENTS
    # -----------------------------
    def _bind_project_events(self):
        self.p_list.bind("<<ListboxSelect>>", self.update_subprojects)

    # -----------------------------
    # PROJECT COLUMN LOGIC
    # -----------------------------
    def get_selected_project(self):
        selection = self.p_list.curselection()
        if selection:
            return self.p_list.get(selection[0])

    def add_project(self):
        p_name = self.pe_ety.get().strip()
        p_names = [item["name"] for item in self.db.get_projects()]

        if p_name in p_names:
            self.error_row.show_error(f"{p_name} already in database!")
        elif len(p_name) == 0:
            self.error_row.show_error("Invalid name")
        else:
            try:
                self.db.post_project(p_name)
                self.pe_ety.delete(0, tk.END)
                self.refresh()
            except psycopg.IntegrityError:
                self.db.conn.rollback()
                messagebox.showerror(
                    "Duplicate Project", f"Project '{p_name}' already exists."
                )
            except Exception as e:
                self.db.conn.rollback()
                messagebox.showerror("Database Error", str(e))

    def update_subprojects(self, event):
        p_name = self.get_selected_project()
        if p_name:
            self.on_project_selected(p_name)

    def update_project(self):
        p_name = self.get_selected_project()

        if p_name:
            try:
                self.db.update_project(p_name)
                self.refresh_status(p_name)
            except psycopg.IntegrityError:
                self.db.conn.rollback()
                messagebox.showerror(
                    "Duplicate Activity",
                    f"Subproject '{p_name}' already has an activity named.",
                )
            except Exception as e:
                self.db.conn.rollback()
                messagebox.showerror("Database Error", str(e))
        else:
            self.error_row.show_error("Select a project first")

    def refresh(self):
        if self.show_all:
            projects = [item["name"] for item in self.db.get_all_projects()]
        else:
            projects = [item["name"] for item in self.db.get_projects()]
        self.p_var.set(projects)

    def refresh_status(self, project):
        project_status = self.db.get_project_status(project)
        if project_status == 1:
            project_status = "Finished"
        else:
            project_status = "Not finished"
        self.ps_var.set(project_status)
